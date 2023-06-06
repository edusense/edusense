'''
Handler to process gaze information from frame and face info
'''

import numpy as np
from datetime import datetime
from utils_computev3 import time_diff, get_logger
from GazeWrapper import GazeInference
from copy import deepcopy
import time
from queue import Empty as EmptyQueueException
import os
import argparse
from multiprocessing.connection import Listener, Client


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Edusense Gaze Handler')
    parser.add_argument('--face_gaze_socket', dest='face_gaze_socket', type=int, nargs='?',
                        help='Socket for tracking-pose process', required=True)
    parser.add_argument('--gaze_output_socket', dest='gaze_output_socket', type=int, nargs='?',
                        help='Socket for pose-output process', required=True)
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
                        nargs='?', default=0.5, help='Rate at which frames are sent to tracking handler')
    # parser.add_argument('--num_face_detection_handlers', dest='num_face_detection_handlers', type=float,
    #                     nargs='?', default=0.5,  help='Rate at which frames are sent to tracking handler')

    args = parser.parse_args()

    session_log_dir = f'cache/logs/{args.course_id}/{args.session_keyword}-{args.session_camera}'
    os.makedirs(session_log_dir, exist_ok=True)
    logger = get_logger('gaze', logdir=session_log_dir)

    # init gaze model
    gaze_model = GazeInference(device=args.device)

    gaze_process_server = Listener(address=('localhost', args.face_gaze_socket), authkey=b'face_gaze')
    time.sleep(20)
    output_process_conn = Client(address=('localhost', args.gaze_output_socket), authkey=b'output')

    face_gaze_conn = gaze_process_server.accept()
    logger.info(f'face_gaze_conn Connection accepted from {gaze_process_server.last_accepted}')

    while True:
        wait_start = datetime.now()
        try:
            frame_number, video_frame, face_results = face_gaze_conn.recv()
        except EmptyQueueException:
            time.sleep(0.5)
            continue
        wait_end = datetime.now()
        if video_frame is None:
            logger.info("Received none frame from input queue, exiting tracking handler.")
            output_process_conn.send((frame_number, 'gaze', None))
            break
        assert (type(video_frame) == np.ndarray) & (len(video_frame.shape) == 3)

        process_start = datetime.now()
        if face_results is not None:
            gaze_results = deepcopy(face_results)
            for body_index, face_result in enumerate(face_results):
                body_bbox = face_result['bbox']
                # logger.info(f'{frame_number},Body: {body_bbox}')
                faces = face_result['face']
                X_TL, Y_TL, X_BR, Y_BR = body_bbox[:4].astype(int)
                if faces.shape[0] > 0:
                    # logger.info(f'{frame_number},Face: {faces[0]}')
                    faces[0][0] += X_TL
                    faces[0][1] += Y_TL
                    faces[0][2] += X_TL
                    faces[0][3] += Y_TL

                    # Get Gaze
                    pred_gazes, _, points_2d, tvecs = gaze_model.run(video_frame, faces, frame_debug=False)
                    gaze_results[body_index].update({
                        'rvec': pred_gazes,
                        'gaze_2d': points_2d,
                        'tvec': tvecs,
                    })

            output_process_conn.send((frame_number, 'gaze', gaze_results))

        process_end = datetime.now()
        logger.info(
            f"Frame: {frame_number}, {time_diff(wait_start, wait_end):.3f} secs | {time_diff(process_start, process_end):.3f} secs")

    gaze_process_server.close()
