'''
This is a livedemo server backend written with streamlit API
'''

import streamlit as st
import logging
import os
import datetime,time
import pandas as pd
import numpy as np
import requests
from livedemo_dockers import init_logger, run_video_docker, run_openpose_docker, kill_containers

logger = init_logger(log_dir='/home/edusense/logs_livedemo')
uid = os.getuid()
gid = os.getgid()


st.title("Edusense Livedemo Interface")

if 'demo_stats' not in st.session_state:
    st.session_state['demo_stats'] = {}

if 'id_ctr' not in st.session_state:
    st.session_state['id_ctr'] = 0

# get camera values
url_in = st.text_input("Camera Address",value="edusense-livedemo.lan.local.cmu.edu",help="Enter Camera URL/IP Address")

with st.container():
    col1,col2 = st.columns(2)
    user_in = col1.text_input("Camera Username", value="admin", help="Enter camera username")
    pass_in = col2.text_input("Camera Password", value="class111_", help="", type="password")
    run_button = col1.button("Run livedemo")
    cleanup_button =col2.button("Server Cleanup")

if run_button:
    st.write("Initializing docker pipeline")
    id = st.session_state['id_ctr']
    rmq_exchange = f'livedemo_exchange_{id}'
    rmq_routing_key = f'livedemo_routing_key_{id}'
    camera_url = f'rtsp://{user_in}:{pass_in}@{url_in}'
    st.write(f"Got Camera Url: {camera_url}")
    video_container_id = run_video_docker(camera_url, rmq_exchange, rmq_routing_key, uid, logger)
    st.write(f"Got video container {video_container_id}")
    time.sleep(5)
    openpose_container_id = run_openpose_docker(camera_url, uid, logger)
    st.write(f"Got openpose container {openpose_container_id}")
    livedemo_stats = {
        'id':id,
        'camera_addr':url_in,
        'camera_user':user_in,
        'camera_pass':pass_in,
        'status':'RUNNING',
        'rmq_exchange':rmq_exchange,
        'rmq_routing_key': rmq_routing_key,
        'video_container':video_container_id,
        'openpose_container':openpose_container_id
    }
    st.session_state['demo_stats'].update({id:livedemo_stats})
    st.session_state['id_ctr']+=1
    st.write("Sending request to flask app")
    response = requests.get(f'http://localhost:8888/add_camera?rmq_exchange={rmq_exchange}&'
                            f'rmq_routing_key={rmq_routing_key}&camera_url={url_in}')
    st.write(f"Post Active Camera Status: {str(response.text)}")

if cleanup_button:
    demo_stats = st.session_state['demo_stats']
    st.write(f"Initializing server cleanup: closing {len(demo_stats.keys())} active pipelines.")
    demo_stats_keys = list(demo_stats.keys())
    for key in demo_stats_keys:
        st.write(f"stopping camera:{demo_stats[key]['camera_addr']}...")
        kill_containers([demo_stats[key]["video_container"], demo_stats[key]["openpose_container"]], logger)
        response = requests.get(f'http://localhost:8888/remove_camera?camera_url={demo_stats[key]["camera_addr"]}')
        del st.session_state['demo_stats'][key]
    st.write("Cleanup complete.")

show_stats_checkbox = st.checkbox("Show Stats")
if show_stats_checkbox:

    for key in st.session_state["demo_stats"]:
        st.header(f"ID: {key}")
        st.write(st.session_state["demo_stats"][key])

