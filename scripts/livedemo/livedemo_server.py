'''
This is a livedemo server backend written with streamlit API
'''

import streamlit as st
import logging
import os
import datetime,time
import pandas as pd
import numpy as np
from livedemo_dockers import init_logger, run_video_docker, run_openpose_docker

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
user_in = st.text_input("Camera Username",value="admin",help="Enter camera username")
pass_in = st.text_input("Camera Password",value="class111_",help="",type="password")

run_button = st.button("Run livedemo")

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
show_stats_checkbox = st.checkbox("Show Stats")

if show_stats_checkbox:

    for key in st.session_state["demo_stats"]:
        st.header(f"ID: {key}")
        st.write(st.session_state["demo_stats"][key])