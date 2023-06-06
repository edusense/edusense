'''
Handler to process video frames and return tracking handler
'''

import numpy as np
from mmtrack.apis import inference_mot, init_model as init_tracking_model
from datetime import datetime
from utils_computev3 import time_diff, get_logger
import time
import os
import argparse
from queue import Empty as EmptyQueueException
from multiprocessing.connection import Listener, Client


def run_tracking_handler(frame_input_queue, pose_queue, face_queue, session_config, logger_name):
    course_id = session_config["course_id"]
    session_keyword, session_camera = session_config["session_keyword"], session_config["session_camera"]
    session_log_dir = f'cache/logs/{course_id}/{session_keyword}-{session_camera}'
    os.makedirs(session_log_dir, exist_ok=True)
    logger = get_logger(logger_name, logdir=session_log_dir)

    # build the model from a config file and a checkpoint file
    tracking_model = init_tracking_model(session_config['track_config'],
                                         session_config['track_checkpoint'],
                                         device=session_config['device'])

    while True:
        wait_start = datetime.now()
        try:
            frame_number, video_frame = frame_input_queue.get(timeout=0.1)
        except EmptyQueueException:
            time.sleep(0.5)
            continue
        wait_end = datetime.now()
        if video_frame is None:
            logger.info("Received none frame from input queue, exiting tracking handler.")
            pose_queue.put((frame_number, None, None))
            num_face_detection_handlers = session_config['num_face_detection_handlers']
            for _ in range(num_face_detection_handlers):
                face_queue.put((frame_number, None, None))
            break

        assert (type(video_frame) == np.ndarray) & (len(video_frame.shape) == 3)

        process_start = datetime.now()

        # get tracking results from video frame
        track_results = inference_mot(tracking_model, video_frame, frame_id=frame_number)
        track_bboxes = track_results['track_bboxes'][0]
        track_results = [dict(bbox=x[1:], track_id=x[0]) for x in list(track_bboxes)]
        if len(track_results) > 0:
            pose_queue.put((frame_number, video_frame, track_results))
            face_queue.put((frame_number, video_frame, track_results))
        process_end = datetime.now()

        logger.info(
            f"Frame: {frame_number}, {time_diff(wait_start, wait_end):.3f} secs | {time_diff(process_start, process_end):.3f} secs")

    return None




if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description='Edusense Video Handler')
    parser.add_argument('--video_tracking_socket', dest='video_tracking_socket', type=int, nargs='?',
                        help='Socket for tracking process', required=True)
    parser.add_argument('--tracking_pose_socket', dest='tracking_pose_socket', type=int, nargs='?',
                        help='Socket for tracking-pose process', required=True)
    parser.add_argument('--tracking_face_socket', dest='tracking_face_socket', type=int, nargs='?',
                        help='Socket for tracking-face process', required=True)
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
    logger = get_logger('tracker', logdir=session_log_dir)

    tracking_config = {
        # trackingHandler
        'track_config': f'{args.source_dir}/configs/mmlab/ocsort_yolox_x_crowdhuman_mot17-private-half.py',
        'track_checkpoint': f'{args.source_dir}/models/mmlab/ocsort_yolox_x_crowdhuman_mot17-private-half_20220813_101618-fe150582.pth',
    }

    # build the model from a config file and a checkpoint file
    tracking_model = init_tracking_model(tracking_config['track_config'],
                                         tracking_config['track_checkpoint'],
                                         device=args.device)
    # get server config for tracking server
    tracking_process_server = Listener(address=('localhost',args.video_tracking_socket), authkey=b'video_tracking')
    time.sleep(20)

    # get client for face and gaze process
    pose_process_conn = Client(address=('localhost',args.tracking_pose_socket), authkey=b'tracking_pose')
    face_process_conn = Client(address=('localhost', args.tracking_face_socket), authkey=b'tracking_face')


    video_tracking_conn = tracking_process_server.accept()
    logger.info(f'video_tracking_conn Connection accepted from {tracking_process_server.last_accepted}')

    while True:
        wait_start = datetime.now()
        try:
            frame_number, video_frame = video_tracking_conn.recv()
        except EmptyQueueException:
            time.sleep(0.5)
            continue
        wait_end = datetime.now()
        if video_frame is None:
            logger.info("Received none frame from input queue, exiting tracking handler.")
            pose_process_conn.send((frame_number, None, None))
            # num_face_detection_handlers = session_config['num_face_detection_handlers']
            # num_face_detection_handlers = 1
            # for _ in range(num_face_detection_handlers):
            #     face_queue.put((frame_number, None, None))
            face_process_conn.send((frame_number, None, None))
            break

        assert (type(video_frame) == np.ndarray) & (len(video_frame.shape) == 3)

        process_start = datetime.now()

        # get tracking results from video frame
        track_results = inference_mot(tracking_model, video_frame, frame_id=frame_number)
        track_bboxes = track_results['track_bboxes'][0]
        track_results = [dict(bbox=x[1:], track_id=x[0]) for x in list(track_bboxes)]
        if len(track_results) > 0:
            pose_process_conn.send((frame_number, video_frame, track_results))
            face_process_conn.send((frame_number, video_frame, track_results))
        process_end = datetime.now()

        logger.info(
            f"Frame: {frame_number}, {time_diff(wait_start, wait_end):.3f} secs | {time_diff(process_start, process_end):.3f} secs")

    tracking_process_server.close()