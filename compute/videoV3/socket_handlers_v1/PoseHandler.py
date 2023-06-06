'''
Handler to process pose information from frame and tracking bboxes
'''

import numpy as np
import mmcv
from mmpose.apis import inference_top_down_pose_model, init_pose_model, vis_pose_result
from datetime import datetime
from utils_computev3 import time_diff, get_logger
import time
from queue import Empty as EmptyQueueException
import argparse
from multiprocessing.connection import Listener, Client
import os


def run_pose_handler(pose_input_queue, pose_output_queue, session_config, logger_name):
    course_id = session_config["course_id"]
    session_keyword, session_camera = session_config["session_keyword"], session_config["session_camera"]
    session_log_dir = f'cache/logs/{course_id}/{session_keyword}-{session_camera}'
    os.makedirs(session_log_dir, exist_ok=True)
    logger = get_logger(logger_name, logdir=session_log_dir)

    # init pose model
    pose_model = init_pose_model(session_config['pose_config'], session_config['pose_checkpoint'],
                                 session_config['device'])
    pose_dataset = pose_model.cfg.data['test']['type']
    pose_dataset_info = pose_model.cfg.data['test'].get('dataset_info', None)
    config_pose = mmcv.Config.fromfile(session_config['pose_config'])

    while True:
        wait_start = datetime.now()
        try:
            frame_number, video_frame, track_results = pose_input_queue.get(timeout=0.1)
        except EmptyQueueException:
            time.sleep(0.5)
            continue

        wait_end = datetime.now()
        if video_frame is None:
            logger.info("Received none frame from input queue, exiting pose handler.")
            pose_output_queue.put((frame_number, 'pose', None))
            break
        assert (type(video_frame) == np.ndarray) & (len(video_frame.shape) == 3)

        h, w, _ = video_frame.shape
        for component in config_pose.data.test.pipeline:
            if component['type'] == 'PoseNormalize':
                component['mean'] = (w // 2, h // 2, .5)
                component['max_value'] = (w, h, 1.)

        process_start = datetime.now()
        if track_results is not None:
            pose_results, _ = inference_top_down_pose_model(pose_model,
                                                            video_frame,
                                                            track_results,
                                                            format='xyxy',
                                                            dataset=pose_dataset,
                                                            dataset_info=pose_dataset_info)

            pose_output_queue.put((frame_number, 'pose', pose_results))

        process_end = datetime.now()

        logger.info(
            f"Frame: {frame_number}, {time_diff(wait_start, wait_end):.3f} secs | {time_diff(process_start, process_end):.3f} secs")

    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Edusense Video Handler')
    parser.add_argument('--tracking_pose_socket', dest='tracking_pose_socket', type=int, nargs='?',
                        help='Socket for tracking-pose process', required=True)
    parser.add_argument('--pose_output_socket', dest='pose_output_socket', type=int, nargs='?',
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
    logger = get_logger('pose', logdir=session_log_dir)

    pose_config = {
        # poseHandler
        'pose_config': f'{args.source_dir}/configs/mmlab/hrnet_w32_coco_256x192.py',
        'pose_checkpoint': f'{args.source_dir}/models/mmlab/hrnet_w32_coco_256x192-c78dce93_20200708.pth',
        'kpt_thr': 0.3,
    }

    # init pose model
    pose_model = init_pose_model(pose_config['pose_config'], pose_config['pose_checkpoint'],
                                 args.device)
    pose_dataset = pose_model.cfg.data['test']['type']
    pose_dataset_info = pose_model.cfg.data['test'].get('dataset_info', None)
    config_pose = mmcv.Config.fromfile(pose_config['pose_config'])


    pose_process_server = Listener(address=('localhost', args.tracking_pose_socket), authkey=b'tracking_pose')
    time.sleep(20)
    output_process_conn = Client(address=('localhost', args.pose_output_socket), authkey=b'output')

    tracking_pose_conn = pose_process_server.accept()
    logger.info(f'tracking_pose_conn Connection accepted from {pose_process_server.last_accepted}')

    while True:
        wait_start = datetime.now()
        try:
            frame_number, video_frame, track_results = tracking_pose_conn.recv()
        except EmptyQueueException:
            time.sleep(0.5)
            continue

        wait_end = datetime.now()
        if video_frame is None:
            logger.info("Received none frame from input queue, exiting pose handler.")
            output_process_conn.send((frame_number, 'pose', None))
            break
        assert (type(video_frame) == np.ndarray) & (len(video_frame.shape) == 3)

        h, w, _ = video_frame.shape
        for component in config_pose.data.test.pipeline:
            if component['type'] == 'PoseNormalize':
                component['mean'] = (w // 2, h // 2, .5)
                component['max_value'] = (w, h, 1.)

        process_start = datetime.now()
        if track_results is not None:
            pose_results, _ = inference_top_down_pose_model(pose_model,
                                                            video_frame,
                                                            track_results,
                                                            format='xyxy',
                                                            dataset=pose_dataset,
                                                            dataset_info=pose_dataset_info)

            output_process_conn.send((frame_number, 'pose', pose_results))

        process_end = datetime.now()
        logger.info(
            f"Frame: {frame_number}, {time_diff(wait_start, wait_end):.3f} secs | {time_diff(process_start, process_end):.3f} secs")

    pose_process_server.close()
