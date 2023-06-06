'''
Handler to process face information from frame and tracking bboxes
'''

import numpy as np
from FaceWrapper import RetinaFaceInference
from datetime import datetime
from utils_computev3 import time_diff, get_logger
from copy import deepcopy
import time
import torch
import os
from queue import Empty as EmptyQueueException
from concurrent.futures import ThreadPoolExecutor
import argparse
from multiprocessing.connection import Listener, Client

def run_face_handler(face_input_queue, gaze_input_queue, face_embedding_input_queue, session_config, logger_name):
    course_id = session_config["course_id"]
    session_keyword, session_camera = session_config["session_keyword"], session_config["session_camera"]
    session_log_dir = f'cache/logs/{course_id}/{session_keyword}-{session_camera}'
    os.makedirs(session_log_dir,exist_ok=True)
    logger = get_logger(logger_name, logdir=session_log_dir)
    # init face boundingbox model
    retinaface = RetinaFaceInference(device=torch.device(session_config['device']))
    # retinaface = RetinaFaceInference(device=torch.device('cuda:1'))
    threadExecutor = ThreadPoolExecutor(5)
    body_count=0
    while True:
        success = False
        wait_start = datetime.now()
        try:
            frame_number, video_frame, track_results = face_input_queue.get(timeout=0.1)
        except EmptyQueueException:
            time.sleep(0.5)
            continue
        wait_end = datetime.now()
        if video_frame is None:
            logger.info("Received none frame from input queue, exiting face detection handler.")
            gaze_input_queue.put((frame_number, None, None))
            face_embedding_input_queue.put((frame_number, None, None))
            break
        assert (type(video_frame) == np.ndarray) & (len(video_frame.shape) == 3)
        h, w, _ = video_frame.shape
        process_start = datetime.now()

        if track_results is not None:
            # face_results = deepcopy(track_results)
            body_count = len(track_results)
            body_frames = []
            body_indexes = []
            for body_index, tracking_info in enumerate(track_results):
                if type(tracking_info) == dict:
                    body_bbox = tracking_info['bbox']
                    X_TL, Y_TL, X_BR, Y_BR = body_bbox[:4].astype(int)
                    if (np.abs(Y_TL-Y_BR)<3) | (np.abs(X_TL-X_BR)<3):
                        logger.warning("Very small body space found, not running face detection...")
                        continue
                    body_frame = video_frame[Y_TL:Y_BR, X_TL:X_BR, :]
                    body_frames.append(body_frame)
                    body_indexes.append(body_index)

            face_detections = threadExecutor.map(retinaface.run, body_frames)
            for body_index, face_result in zip(body_indexes,face_detections):
                track_results[body_index].update({
                    'face':face_result[0]
                })
            # faces, _ = [retinaface.run(body_frame, frame_debug=None)[0] for body_frame in body_frames]
            # face_results[body_index].update({
            #     'face':faces
            # })

            gaze_input_queue.put((frame_number, video_frame, track_results))
            face_embedding_input_queue.put((frame_number, video_frame, track_results))
            success = True

        process_end = datetime.now()
        logger.info(
            f"Frame: {frame_number}, {time_diff(wait_start, wait_end):.3f} secs | {time_diff(process_start, process_end):.3f} secs [{body_count}]")

    return None




if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description='Edusense Video Handler')
    parser.add_argument('--tracking_face_socket', dest='tracking_face_socket', type=int, nargs='?',
                        help='Socket for tracking-face process', required=True)
    parser.add_argument('--face_gaze_socket', dest='face_gaze_socket', type=int, nargs='?',
                        help='Socket for face-gaze process', required=True)
    # parser.add_argument('--face_emb_socket', dest='face_emb_socket', type=int, nargs='?',
    #                     help='Socket for face-emb process', required=True)
    parser.add_argument('--source_dir', dest='source_dir', type=str, nargs='?',
                        help='root directory for run', required=True)
    parser.add_argument('--course_id', dest='course_id', type=str, nargs='?',
                        help='course id', required=True)
    parser.add_argument('--session_dir', dest='session_dir', type=str, nargs='?',
                        help='Directory path for given session ID for processing session')
    parser.add_argument('--session_keyword', dest='session_keyword', type=str, nargs='?',
                        help='Session ID for processing session')
    parser.add_argument('--session_camera', dest='session_camera', type=str, nargs='?',
                        help='Camera(front/back) for given session id')
    parser.add_argument('--device', dest='device', type=str, nargs='?',
                        help='GPU id to deploy model')
    parser.add_argument('--target_fps', dest='target_fps', type=int,
                        nargs='?', default=3, help='Rate at which video is processed')
    parser.add_argument('--frame_interval', dest='frame_interval', type=float,
                        nargs='?', default=0.5,  help='Rate at which frames are sent to tracking handler')
    # parser.add_argument('--num_face_detection_handlers', dest='num_face_detection_handlers', type=float,
    #                     nargs='?', default=0.5,  help='Rate at which frames are sent to tracking handler')

    args = parser.parse_args()

    session_log_dir = f'cache/logs/{args.course_id}/{args.session_keyword}-{args.session_camera}'
    os.makedirs(session_log_dir, exist_ok=True)
    logger = get_logger('face', logdir=session_log_dir)


    retinaface = RetinaFaceInference(device=torch.device(args.device))
    # retinaface = RetinaFaceInference(device=torch.device('cuda:1'))
    threadExecutor = ThreadPoolExecutor(5)
    body_count=0

    # get server config for tracking server
    face_process_server = Listener(address=('localhost',args.tracking_face_socket), authkey=b'tracking_face')
    time.sleep(20)

    # get client for face and gaze process
    gaze_process_conn = Client(address=('localhost',args.face_gaze_socket), authkey=b'face_gaze')
    # face_emb_process_conn = Client(address=('localhost',args.face_emb_socket), authkey=b'face_emb')

    tracking_face_conn = face_process_server.accept()
    logger.info(f'tracking_face_conn Connection accepted from {face_process_server.last_accepted}')

    while True:
        success = False
        wait_start = datetime.now()
        try:
            frame_number, video_frame, track_results = tracking_face_conn.recv()
        except EmptyQueueException:
            time.sleep(0.5)
            continue
        wait_end = datetime.now()
        if video_frame is None:
            logger.info("Received none frame from input queue, exiting face detection handler.")
            gaze_process_conn.send((frame_number, None, None))
            # face_emb_process_conn.send((frame_number, None, None))
            break
        assert (type(video_frame) == np.ndarray) & (len(video_frame.shape) == 3)
        h, w, _ = video_frame.shape
        process_start = datetime.now()

        if track_results is not None:
            # face_results = deepcopy(track_results)
            body_count = len(track_results)
            body_frames = []
            body_indexes = []
            for body_index, tracking_info in enumerate(track_results):
                if type(tracking_info) == dict:
                    body_bbox = tracking_info['bbox']
                    X_TL, Y_TL, X_BR, Y_BR = body_bbox[:4].astype(int)
                    if (np.abs(Y_TL-Y_BR)<3) | (np.abs(X_TL-X_BR)<3):
                        logger.warning("Very small body space found, not running face detection...")
                        continue
                    body_frame = video_frame[Y_TL:Y_BR, X_TL:X_BR, :]
                    body_frames.append(body_frame)
                    body_indexes.append(body_index)

            face_detections = threadExecutor.map(retinaface.run, body_frames)
            for body_index, face_result in zip(body_indexes,face_detections):
                track_results[body_index].update({
                    'face':face_result[0]
                })
            # faces, _ = [retinaface.run(body_frame, frame_debug=None)[0] for body_frame in body_frames]
            # face_results[body_index].update({
            #     'face':faces
            # })

            gaze_process_conn.send((frame_number, video_frame, track_results))
            # face_emb_process_conn.send((frame_number, video_frame, track_results))
            success = True

        process_end = datetime.now()
        logger.info(
            f"Frame: {frame_number}, {time_diff(wait_start, wait_end):.3f} secs | {time_diff(process_start, process_end):.3f} secs [{body_count}]")

    face_process_server.close()
