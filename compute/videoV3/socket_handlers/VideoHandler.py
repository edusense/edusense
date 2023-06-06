'''
Handler to process video into frames and passing to tracking processes
'''

import mmcv
import time
from queue import Empty as EmptyQueueException
from multiprocessing.connection import Listener, Client
from utils_computev3 import time_diff, get_logger
import os
import argparse

if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description='Edusense Video Handler')
    parser.add_argument('--video_tracking_socket', dest='video_tracking_socket', type=int, nargs='?',
                        help='Socket for tracking process', required=True)
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
    args = parser.parse_args()

    session_log_dir = f'cache/logs/{args.course_id}/{args.session_keyword}-{args.session_camera}'
    os.makedirs(session_log_dir, exist_ok=True)
    logger = get_logger('video', logdir=session_log_dir)

    class_video_file = f'{args.session_dir}/{args.session_keyword}-{args.session_camera}.avi'
    mmcv_video_frames = mmcv.VideoReader(class_video_file)
    video_fps = mmcv_video_frames.fps
    # target_fps = session_config['target_fps']
    # start_frame_number, frame_interval = session_config['start_frame_number'], session_config['frame_interval']

    h, w, _ = mmcv_video_frames[0].shape

    logger.info("reading frames from video")

    # session_config.update({
    #     'frame_width': w,
    #     'frame_height': h,
    #     'fps': target_fps,
    # })
    num_skip_frames = int(video_fps / args.target_fps)
    logger.info(f"Target FPS: {args.target_fps}, Video FPS: {video_fps}, Num Skip Frames: {num_skip_frames}")
    time.sleep(10)
    # get client for tracking process
    tracking_process_conn = Client(address=('localhost',args.video_tracking_socket), authkey=b'video_tracking')
    # time.sleep(600)
    for frame_number, video_frame in enumerate(mmcv_video_frames):
        if (num_skip_frames == 0) | (frame_number % num_skip_frames == 0):
            # frame_output_queue.put((frame_number, video_frame))
            tracking_process_conn.send((frame_number, video_frame))
            logger.info(f"pushed frame {frame_number}")
            if args.frame_interval >0.:
                time.sleep(args.frame_interval)

    tracking_process_conn.send((frame_number, None))
    logger.info("Finished video process, exiting...")




