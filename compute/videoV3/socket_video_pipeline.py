"""
This is main file to run Edusense pipeline with compute V3 on multiprocessing
"""
import os
import sys

from configs.get_session_config import get_session_config
from utils_computev3 import get_logger, time_diff
from multiprocessing.connection import Listener, Client
from multiprocessing import Process, Queue
import socket_handlers
import torch
import threading
from subprocess import Popen

from queue import Empty as EmptyQueueException
import time
import pickle
import glob

SOURCE_DIR = '/home/prasoon/openmmlab/edusenseV2compute/compute/videoV3'
VIDEO_DIR = '/mnt/ci-nas-classes/classinsight/2019F/video_backup'
COURSE_ID = '79388A'
INIT_SOCKET_ADDRESS =8000
# COURSE_ID = ''
OUT_DIR = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV3/cache/video'
BACKFILL_STATUS_DIR = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV3/cache/backfill_status'
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(BACKFILL_STATUS_DIR, exist_ok=True)
# SESSION_DIR = '/mnt/ci-nas-classes/classinsight/2019F/video_backup'
# SESSION_KEYWORD = 'classinsight-cmu_79388A_ghc_4301_201910031826'
# SESSION_CAMERA = 'front'
# SOURCE_DIR = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV3'
# SESSION_DIR = '/home/prasoon/video_analysis/mmtracking/'
# SESSION_KEYWORD = 'first-10-min_5fps.mp4'

DEVICE = 'cuda:4'

NUM_FACE_DETECTION_HANDLERS = 1
TARGET_FPS = 3
# START_FRAME_NUMBER = 0 # used for debug purposes only
FRAME_INTERVAL_IN_SEC = 0.5
MAX_QUEUE_SIZE = 300
session_dirs = glob.glob(f'{VIDEO_DIR}/*')
session_dirs = [xr for xr in session_dirs if f'_{COURSE_ID}_' in xr]
print(f"Got {len(session_dirs)} sessions from {VIDEO_DIR} and course {COURSE_ID}")

if __name__ == '__main__':
    # try:
    #     torch.multiprocessing.set_start_method('spawn')
    # except:
    #     print("Spawn method already set, continue...")
    for SESSION_DIR in session_dirs:
        SESSION_KEYWORD = SESSION_DIR.split("/")[-1]
        for SESSION_CAMERA in ['front']:
            session_log_dir = f'cache/logs/{COURSE_ID}/{SESSION_KEYWORD}-{SESSION_CAMERA}'
            os.makedirs(session_log_dir, exist_ok=True)
            logger = get_logger(f"main", logdir=session_log_dir)
            logger.info(f"processing for session {SESSION_KEYWORD}, {SESSION_CAMERA}")
            t_start_session = time.time()
            session_config = get_session_config(SOURCE_DIR,
                                                COURSE_ID,
                                                SESSION_DIR,
                                                SESSION_KEYWORD,
                                                SESSION_CAMERA,
                                                DEVICE,
                                                TARGET_FPS,
                                                start_frame_number=0,
                                                frame_interval=FRAME_INTERVAL_IN_SEC)

            session_config['num_face_detection_handlers'] = NUM_FACE_DETECTION_HANDLERS

            # Check if session camera output file exists in output dir
            session_keyword, session_camera = session_config["session_keyword"], session_config["session_camera"]

            session_backfill_status_file = f'{BACKFILL_STATUS_DIR}/{session_keyword}-{session_camera}.txt'
            backfill_completion_status = 'backfill_complete...'
            if os.path.exists(session_backfill_status_file):
                with open(session_backfill_status_file, 'r') as f:
                    most_recent_stats = f.readlines()[-1]
                    if most_recent_stats == backfill_completion_status:
                        logger.info(f"Session backfilled already. Skipping..")
                        continue
                    else:
                        logger.info(f"Session backfill status partial...")
                logger.info(f"Session starting fresh backfilling...")
                os.remove(session_backfill_status_file)

            # Setup multiprocessing queues <input>_<output>_queue
            '''                        
            Queue-Process Architecture:

            P:video_handler
                   |
                  \|/                                   |--Q{tracking_pose_queue}--> P:pose_handler ------------>|
            Q{video_tracking_queue}-> P:tracking_handler|                                                        |
                                                        |--Q{tracking_face_queue}-->P:face_handler               |
                                                                                         |                       |--Q{video_output_queue}-->
                                                                                        \|/                      |
                                                                                          --Q{face_gaze_queue}-->|
                                                                                          --Q{face_emb_queue}--->|

            '''

            VIDEO_TRACKING_SOCKET = INIT_SOCKET_ADDRESS
            TRACKING_POSE_SOCKET = INIT_SOCKET_ADDRESS+1
            TRACKING_FACE_SOCKET = INIT_SOCKET_ADDRESS+2
            FACE_GAZE_SOCKET = INIT_SOCKET_ADDRESS+3
            FACE_EMB_SOCKET = INIT_SOCKET_ADDRESS+4
            VIDEO_OUTPUT_SOCKET = INIT_SOCKET_ADDRESS+5

            output_server = Listener(address=('localhost', VIDEO_OUTPUT_SOCKET), authkey=b'output')

            common_command_args = f'--source_dir {SOURCE_DIR} --course_id {COURSE_ID} --session_dir {SESSION_DIR} --session_keyword {SESSION_KEYWORD} ' \
                                  f'--session_camera {SESSION_CAMERA} --device {DEVICE} --target_fps {TARGET_FPS} ' \
                                  f'--frame_interval {FRAME_INTERVAL_IN_SEC}'.split(" ")

            gaze_command_args = f'python socket_handlers/GazeHandler.py --face_gaze_socket {FACE_GAZE_SOCKET} ' \
                                f'--gaze_output_socket {VIDEO_OUTPUT_SOCKET}'.split(" ") + common_command_args
            gaze_process = Popen(gaze_command_args)

            face_command_args = f'python socket_handlers/FaceDetectionHandler.py --tracking_face_socket {TRACKING_FACE_SOCKET} ' \
                                f'--face_gaze_socket {FACE_GAZE_SOCKET}'.split(" ") + common_command_args
            face_process = Popen(face_command_args)

            pose_command_args = f'python socket_handlers/PoseHandler.py --tracking_pose_socket {TRACKING_POSE_SOCKET} ' \
                                f'--pose_output_socket {VIDEO_OUTPUT_SOCKET}'.split(" ") + common_command_args
            pose_process = Popen(pose_command_args)

            tracking_command_args = f'python socket_handlers/TrackingHandler.py --video_tracking_socket {VIDEO_TRACKING_SOCKET} ' \
                                    f'--tracking_pose_socket {TRACKING_POSE_SOCKET} --tracking_face_socket {TRACKING_FACE_SOCKET}'.split(" ") + common_command_args
            tracking_process = Popen(tracking_command_args)

            logger.info("Sleeping for 10 secs to let pose and tracking processes start")
            time.sleep(20)

            # define client handler
            def output_client_handler(client_connection, output_queue):
                time.sleep(1)
                while True:
                    frame_number, frame_type, frame_data = client_connection.recv()
                    output_queue.put((frame_number, frame_type, frame_data))
                    if frame_data is None:
                        break
                client_connection.close()

            out_queue = Queue()

            # accept connection from 2 clients and start threads
            i = 0
            output_connections = []
            while(i<2):
                output_conn = output_server.accept()
                logger.info(f'output_conn Connection accepted from {output_server.last_accepted}')
                client_process = Process(target=output_client_handler, args=(output_conn, out_queue))
                # client_process.start()
                output_connections.append(client_process)
                i+=1

            # start video reading
            video_command_args = f'python socket_handlers/VideoHandler.py --video_tracking_socket {VIDEO_TRACKING_SOCKET}'.split(
                " ") + common_command_args
            video_process = Popen(video_command_args)

            for i in range(len(output_connections)):
                output_connections[i].start()

            session_video_output = {
                'gaze': [],
                'face_embedding': [],
                'pose': []
            }

            final_packet_received = {'gaze': False, 'face_embedding': False, 'pose': False}

            output_start_time = time.time()
            while True:
                try:
                    frame_number, frame_type, frame_data = out_queue.get(timeout=0.5)
                except EmptyQueueException:
                    time.sleep(0.5)
                    logger.info("Empty Output Queue")
                    continue
                if frame_type not in session_video_output.keys():
                    logger.info(f"Frame Type {frame_type} is not supported..")
                    continue
                if frame_data is None:
                    final_packet_received[frame_type] = True
                    if (final_packet_received['gaze']) & (final_packet_received['pose']) & (
                            final_packet_received['face_embedding']):
                        logger.info("All frames received, closing output handler...")
                        session_output_file = f'{OUT_DIR}/{session_keyword}-{session_camera}.pb'
                        pickle.dump(session_video_output, open(session_output_file, 'wb'))
                        with open(session_backfill_status_file, 'a+') as f:
                            f.write(backfill_completion_status)
                        break
                else:
                    session_video_output[frame_type].append((frame_number, frame_data))
                if (frame_number % 1000 == 0) & (frame_type == 'face_embedding'):
                    with open(session_backfill_status_file, 'a+') as f:
                        f.write(f'{frame_number}-{time.time() - output_start_time:3f}')
                    logger.info(f"Stored frames till {frame_number} in {time.time() - output_start_time:3f} secs..")
                    output_start_time = time.time()

            output_server.close()
            sys.exit(0)
