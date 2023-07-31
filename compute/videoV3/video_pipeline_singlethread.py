'''
This is new edusense pipeline, given a video, we generate tracking id first, and then shift to pose and face bb detection.
Once detected, we use gaze module to extract gaze information, and facial features network to extract facial features.

This is followed by all inferences from older video pipeline
'''

import os
import sys

from configs.get_session_config import get_session_config
from utils_computev3 import get_logger, time_diff
from mmtrack.apis import inference_mot, init_model as init_tracking_model
import mmcv
from mmpose.apis import inference_top_down_pose_model, init_pose_model, vis_pose_result
from datetime import datetime
from FaceWrapper import RetinaFaceInference
from utils_computev3 import time_diff, get_logger
from concurrent.futures import ThreadPoolExecutor
from GazeWrapper import GazeInference
from facenet_pytorch import InceptionResnetV1
import time
import os
import argparse
import torch
import threading
from subprocess import Popen
import numpy as np
from queue import Empty as EmptyQueueException
import time
import pickle
import glob
import tensorflow as tf
import cv2
tf_version = tf.__version__
tf_major_version = int(tf_version.split(".", maxsplit=1)[0])
tf_minor_version = int(tf_version.split(".")[1])

if tf_major_version == 1:
    from keras.preprocessing import image
elif tf_major_version == 2:
    from tensorflow.keras.preprocessing import image


SOURCE_DIR = '/home/prasoon/openmmlab/edusenseV2compute/compute/videoV3'
VIDEO_DIR = '/mnt/ci-nas-classes/classinsight/2019F/video_backup'
# COURSE_ID = '79388A'
# COURSE_ID = '82235A'
COURSE_ID = '82119A'
# COURSE_ID = sys.argv[1]
# DEVICE_ARG = int(sys.argv[2])
DEVICE_ARG = 1
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

DEVICE = f'cuda:{DEVICE_ARG}'
DEVICE_FACE = f'cuda:{DEVICE_ARG+1}'
FACE_NUM_POOL_WORKERS = 10
TARGET_FPS = 5
# START_FRAME_NUMBER = 0 # used for debug purposes only
FRAME_INTERVAL_IN_SEC = 0.5
MAX_QUEUE_SIZE = 300
session_dirs = glob.glob(f'{VIDEO_DIR}/*')
session_dirs = [xr for xr in session_dirs if f'_{COURSE_ID}_' in xr]
print(f"Got {len(session_dirs)} sessions from {VIDEO_DIR} and course {COURSE_ID}")


if __name__ == '__main__':
    for SESSION_DIR in session_dirs:
        SESSION_KEYWORD = SESSION_DIR.split("/")[-1]
        for SESSION_CAMERA in ['front']:

            # get logger
            session_log_dir = f'cache/single_thread/logs/{COURSE_ID}'
            os.makedirs(session_log_dir, exist_ok=True)
            logger = get_logger(f"{SESSION_KEYWORD}-{SESSION_CAMERA}", logdir=session_log_dir)
            logger.info(f"processing for session {SESSION_KEYWORD}, {SESSION_CAMERA}")

            # initialize session config
            session_frames_output_dir = f'cache/single_thread/output/{COURSE_ID}/{SESSION_KEYWORD}-{SESSION_CAMERA}'
            os.makedirs(session_frames_output_dir, exist_ok=True)
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
            # setup networks for tracking, pose, face, gaze and embedding handlers

            # -------Tracking Model init-------
            tracking_config = {
                # trackingHandler
                'track_config': f'{SOURCE_DIR}/configs/mmlab/ocsort_yolox_x_crowdhuman_mot17-private-half.py',
                'track_checkpoint': f'{SOURCE_DIR}/models/mmlab/ocsort_yolox_x_crowdhuman_mot17-private-half_20220813_101618-fe150582.pth',
            }
            tracking_model = init_tracking_model(tracking_config['track_config'],
                                                 tracking_config['track_checkpoint'],
                                                 device=DEVICE)

            # -------pose Model init-------
            pose_config = {
                # poseHandler
                'pose_config': f'{SOURCE_DIR}/configs/mmlab/hrnet_w32_coco_256x192.py',
                'pose_checkpoint': f'{SOURCE_DIR}/models/mmlab/hrnet_w32_coco_256x192-c78dce93_20200708.pth',
                'kpt_thr': 0.3,
            }
            pose_model = init_pose_model(pose_config['pose_config'], pose_config['pose_checkpoint'],
                                         DEVICE)
            pose_dataset = pose_model.cfg.data['test']['type']
            pose_dataset_info = pose_model.cfg.data['test'].get('dataset_info', None)
            config_pose = mmcv.Config.fromfile(pose_config['pose_config'])

            # -------face Model init-------
            face_model = RetinaFaceInference(device=torch.device(DEVICE_FACE))
            face_threadExecutor = ThreadPoolExecutor(FACE_NUM_POOL_WORKERS)
            body_count = 0

            # -------gaze and embedding Model init-------
            gaze_model = GazeInference(device=DEVICE)
            facial_embedding_model = InceptionResnetV1(pretrained=session_config['face_embedding_model_name'],
                                                       device=DEVICE).eval()

            # start loop with frames and video handler
            class_video_file = f'{SESSION_DIR}/{SESSION_KEYWORD}-{SESSION_CAMERA}.avi'
            mmcv_video_frames = mmcv.VideoReader(class_video_file)
            video_fps = mmcv_video_frames.fps
            h, w, _ = mmcv_video_frames[0].shape
            logger.info("reading frames from video")
            num_skip_frames = int(video_fps / TARGET_FPS)
            session_process_start = datetime.now()
            for frame_number, video_frame in enumerate(mmcv_video_frames):
                if (num_skip_frames == 0) | (frame_number % num_skip_frames == 0):
                    frame_process_start = datetime.now()

                    # get tracking output
                    track_process_start = datetime.now()
                    track_results = inference_mot(tracking_model, video_frame, frame_id=frame_number)
                    track_bboxes = track_results['track_bboxes'][0]
                    track_results = [dict(bbox=x[1:], track_id=x[0]) for x in list(track_bboxes)]
                    track_process_end = datetime.now()
                    logger.info(
                        f"Frame: {frame_number} | track | {time_diff(track_process_start, track_process_end):.3f} secs")

                    # get pose output
                    pose_process_start = datetime.now()
                    h, w, _ = video_frame.shape
                    for component in config_pose.data.test.pipeline:
                        if component['type'] == 'PoseNormalize':
                            component['mean'] = (w // 2, h // 2, .5)
                            component['max_value'] = (w, h, 1.)

                    process_start = datetime.now()
                    if track_results is not None:
                        frame_results, _ = inference_top_down_pose_model(pose_model,
                                                                        video_frame,
                                                                        track_results,
                                                                        format='xyxy',
                                                                        dataset=pose_dataset,
                                                                        dataset_info=pose_dataset_info)
                    else:
                        frame_results=None
                    pose_process_end = datetime.now()
                    logger.info(f"Frame: {frame_number} | pose | {time_diff(pose_process_start, pose_process_end):.3f} secs")

                    # get face output
                    face_process_start = datetime.now()

                    if frame_results is not None:
                        # face_results = deepcopy(frame_results)
                        body_count = len(frame_results)
                        body_frames = []
                        body_indexes = []
                        for body_index, tracking_info in enumerate(frame_results):
                            if type(tracking_info) == dict:
                                body_bbox = tracking_info['bbox']
                                X_TL, Y_TL, X_BR, Y_BR = body_bbox[:4].astype(int)
                                if ((Y_BR - Y_TL) < 5) | ((X_BR - X_TL) < 5):
                                    logger.warning("Very small body space found, not running face detection...")
                                    continue

                                body_frame = video_frame[Y_TL:Y_BR, X_TL:X_BR, :]
                                body_frames.append(body_frame)
                                body_indexes.append(body_index)

                        face_detections = face_threadExecutor.map(face_model.run, body_frames)
                        for body_index, face_result in zip(body_indexes, face_detections):
                            frame_results[body_index].update({
                                'face': face_result[0]
                            })

                    face_process_end = datetime.now()
                    logger.info(
                        f"Frame: {frame_number} | face | {time_diff(face_process_start, face_process_end):.3f} secs [{body_count}]")

                    # get gaze output
                    gaze_process_start = datetime.now()
                    if frame_results is not None:
                        for body_index, frame_result in enumerate(frame_results):
                            body_bbox = frame_result['bbox']
                            # logger.info(f'{frame_number},Body: {body_bbox}')
                            faces = frame_result.get('face',np.array([]))
                            X_TL, Y_TL, X_BR, Y_BR = body_bbox[:4].astype(int)
                            if faces.shape[0] > 0:
                                # logger.info(f'{frame_number},Face: {faces[0]}')
                                faces[0][0] += X_TL
                                faces[0][1] += Y_TL
                                faces[0][2] += X_TL
                                faces[0][3] += Y_TL

                                # Get Gaze
                                pred_gazes, _, points_2d, tvecs = gaze_model.run(video_frame, faces, frame_debug=False)
                                frame_results[body_index].update({
                                    'rvec': pred_gazes,
                                    'gaze_2d': points_2d,
                                    'tvec': tvecs,
                                })
                    gaze_process_end = datetime.now()
                    logger.info(
                        f"Frame: {frame_number} | gaze | {time_diff(gaze_process_start, gaze_process_end):.3f} secs")

                    # get facial embedding output

                    emb_process_start = datetime.now()
                    if frame_results is not None:
                        for body_index, frame_result in enumerate(frame_results):
                            body_bbox = frame_result['bbox']
                            faces = frame_result.get('face',np.array([]))
                            X_TL, Y_TL, X_BR, Y_BR = body_bbox[:4].astype(int)
                            if faces.shape[0] > 0:
                                faces[0][0] += X_TL
                                faces[0][1] += Y_TL
                                faces[0][2] += X_TL
                                faces[0][3] += Y_TL

                                # Get facial embedding for given face.
                                faces = faces[0][:4].astype(int)
                                face_frame = video_frame[faces[1]:faces[3], faces[0]:faces[2], :]
                                target_size = (244, 244)

                                if face_frame.shape[0] > 0 and face_frame.shape[1] > 0:
                                    factor_0 = target_size[0] / face_frame.shape[0]
                                    factor_1 = target_size[1] / face_frame.shape[1]
                                    factor = min(factor_0, factor_1)

                                    dsize = (int(face_frame.shape[1] * factor), int(face_frame.shape[0] * factor))
                                    face_frame = cv2.resize(face_frame, dsize)

                                    diff_0 = target_size[0] - face_frame.shape[0]
                                    diff_1 = target_size[1] - face_frame.shape[1]

                                    # Put the base image in the middle of the padded image
                                    face_frame = np.pad(
                                        face_frame,
                                        (
                                            (diff_0 // 2, diff_0 - diff_0 // 2),
                                            (diff_1 // 2, diff_1 - diff_1 // 2),
                                            (0, 0),
                                        ),
                                        "constant",
                                    )
                                    # double check: if target image is not still the same size with target.
                                    if face_frame.shape[0:2] != target_size:
                                        face_frame = cv2.resize(face_frame, target_size)

                                    # normalizing the image pixels
                                    video_frame_pixels = face_frame.astype(np.float32)  # what this line doing? must?
                                    video_frame_pixels /= 255  # normalize input in [0, 1]
                                    face_tensor = torch.from_numpy(video_frame_pixels).permute(2, 1, 0).unsqueeze(0).to(
                                        session_config['device'])
                                    face_embedding = facial_embedding_model(face_tensor)[0].to('cpu').detach().numpy()
                                    frame_results[body_index].update({
                                        'face_embedding': face_embedding
                                    })
                    emb_process_end = datetime.now()

                    logger.info(
                        f"Frame: {frame_number} | embedding | {time_diff(emb_process_start, emb_process_end):.3f} secs")

                    # output frame in frames dir
                    pickle.dump(frame_results, open(f'{session_frames_output_dir}/{frame_number}.pb','wb'))

                    frame_process_end = datetime.now()
                    logger.info(
                        f"Frame: {frame_number} | total | {time_diff(frame_process_start, frame_process_end):.3f} secs"
                        f" | {time_diff(session_process_start, frame_process_end):.3f} secs")
