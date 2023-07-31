'''
This is new edusense pipeline, given a list of session videos and corresponding tracking data location, we generate face, gaze and embedding information.
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
import shutil
import traceback

tf_version = tf.__version__
tf_major_version = int(tf_version.split(".", maxsplit=1)[0])
tf_minor_version = int(tf_version.split(".")[1])

if tf_major_version == 1:
    from keras.preprocessing import image
elif tf_major_version == 2:
    from tensorflow.keras.preprocessing import image

# cd /home/prasoon/openmmlab/edusenseV2compute/compute/videoV3/ && conda activate edusense && export PYTHONPATH="${PYTHONPATH}:/home/prasoon/openmmlab/edusenseV2compute/compute/videoV3/"
session_filter_list = ['classinsight-cmu_05681A_ghc_4301_201905011630',
 'classinsight-cmu_05681A_ghc_4301_201904171630',
 'classinsight-cmu_05681A_ghc_4301_201902201630',
 'classinsight-cmu_05681A_ghc_4301_201904101630',
 'classinsight-cmu_05681A_ghc_4301_201901231630',
 'classinsight-cmu_05418A_ghc_4102_201902251200',
 'classinsight-cmu_05418A_ghc_4102_201904081200',
 'classinsight-cmu_05418A_ghc_4102_201905011200',
 'classinsight-cmu_05418A_ghc_4102_201904291200',
 'classinsight-cmu_05418A_ghc_4102_201904011200',
 'classinsight-cmu_05748A_ghc_4101_201902141630',
 'classinsight-cmu_05748A_ghc_4101_201904021630',
 'classinsight-cmu_05748A_ghc_4101_201902051630',
 'classinsight-cmu_05748A_ghc_4101_201902281630',
 'classinsight-cmu_05748A_ghc_4101_201903071630',
 'classinsight-cmu_21127J_ghc_4102_201904230930',
 'classinsight-cmu_21127J_ghc_4102_201903260930',
 'classinsight-cmu_21127J_ghc_4102_201904160930',
 'classinsight-cmu_21127J_ghc_4102_201904300930',
 'classinsight-cmu_21127J_ghc_4102_201903190930',
 'classinsight-cmu_05410A_ghc_4301_201904151500',
 'classinsight-cmu_05410A_ghc_4301_201902251500',
 'classinsight-cmu_05410A_ghc_4301_201904081500',
 'classinsight-cmu_05410A_ghc_4301_201904221500',
 'classinsight-cmu_05410A_ghc_4301_201902181500',
                       
 'classinsight-cmu_17214B_ph_a21_201902271030',
 'classinsight-cmu_17214B_ph_a21_201903061030',
 'classinsight-cmu_17214B_ph_a21_201904031030',
 'classinsight-cmu_17214B_ph_a21_201904101030',
 'classinsight-cmu_17214B_ph_a21_201904241030',
 'classinsight-cmu_17214C_ph_225b_201904031130',
 'classinsight-cmu_17214C_ph_225b_201904101130',
 'classinsight-cmu_17214C_ph_225b_201904171130',
 'classinsight-cmu_17214C_ph_225b_201904241130',
 'classinsight-cmu_17214C_ph_225b_201905011130',
 'classinsight-cmu_05410B_ghc_4211_201902111500',
 'classinsight-cmu_05410B_ghc_4211_201903181500',
 'classinsight-cmu_05410B_ghc_4211_201904081500',
 'classinsight-cmu_05410B_ghc_4211_201904151500',
 'classinsight-cmu_05410B_ghc_4211_201904221500',
 'classinsight-cmu_05410B_ghc_4211_201901281500'
]

SOURCE_DIR = '/home/prasoon/openmmlab/edusenseV2compute/compute/videoV3'
VIDEO_DIR = f'/mnt/ci-nas-classes/classinsight/{sys.argv[1]}/video_backup'
COURSE_ID = sys.argv[2]
DEVICE_ARG = int(sys.argv[3])
DEVICE_FACE_ARG = int(sys.argv[4])
DEVICE = f'cuda:{DEVICE_ARG}'
DEVICE_FACE = f'cuda:{DEVICE_FACE_ARG}'
TARGET_FPS = 5
FRAME_INTERVAL_IN_SEC = 0.5
FACE_NUM_POOL_WORKERS = 5
session_dirs = glob.glob(f'{VIDEO_DIR}/*')
TRACK_INFO_DIR = f'/mnt/ci-nas-cache/edulyzeV2/track/{COURSE_ID}'
print(f"Got {len(session_dirs)} sessions from {VIDEO_DIR}.")
session_dirs = [xr for xr in session_dirs if f'_{COURSE_ID}_' in xr]
# session_dirs = [xr for xr in session_dirs if (xr.split("/")[-1] in session_filter_list)]
print(f"Got {len(session_dirs)} sessions from {VIDEO_DIR} and course {COURSE_ID}")

# initialize NN Models
session_config = {
        # faceEmbeddingHandler
        'face_embedding_model_name':'vggface2',
        'device': DEVICE
}
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

if __name__ == '__main__':
    for SESSION_DIR in session_dirs:
        SESSION_KEYWORD = SESSION_DIR.split("/")[-1]
        for SESSION_CAMERA in ['front']:
            SESSION_CAMERA_FILES = glob.glob(f'{SESSION_DIR}/*{SESSION_CAMERA}.avi')
            for SESSION_CAMERA_FILE in SESSION_CAMERA_FILES:
                SESSION_KEYWORD = \
                SESSION_CAMERA_FILE.split("/")[-1].split(f"_{SESSION_CAMERA}.avi")[0].split(f"-{SESSION_CAMERA}.avi")[0]
                
                # get logger
                session_log_dir = f'cache/logs_embedding_singlethread/{COURSE_ID}'
                os.makedirs(session_log_dir, exist_ok=True)
                logger = get_logger(f"{SESSION_KEYWORD}-{SESSION_CAMERA}", logdir=session_log_dir)
                logger.info(f"processing for session {SESSION_KEYWORD}, {SESSION_CAMERA}")

                # initialize session config
                session_frames_output_dir = f'/mnt/ci-nas-cache/edulyzeV2/pose_face_gaze_emb/{COURSE_ID}/{SESSION_KEYWORD}-{SESSION_CAMERA}'
                if os.path.exists(session_frames_output_dir):
                    if os.path.exists(f"{session_frames_output_dir}/end.pb"):
                        logger.info(f"session tracking output dir exists with end file, Delete it to rerun the session.")
                        continue
                    else:
                        logger.info(
                            f"session tracking output dir exists but no end file, Deleting it and rerunning the session.")
                        shutil.rmtree(session_frames_output_dir)
                os.makedirs(session_frames_output_dir, exist_ok=True)
                t_start_session = time.time()

                # start loop with frames and video handler
                class_video_file = f'{SESSION_DIR}/{SESSION_KEYWORD}-{SESSION_CAMERA}.avi'
                class_video_file = SESSION_CAMERA_FILE
                if not os.path.exists(class_video_file):
                    logger.info(f"Video File {class_video_file} not available, skipping session...")
                    continue
                mmcv_video_frames = mmcv.VideoReader(class_video_file)
                video_fps = mmcv_video_frames.fps
                # h, w, _ = mmcv_video_frames[0].shape
                logger.info("reading frames from video")
                num_skip_frames = int(video_fps / TARGET_FPS)
                session_process_start = datetime.now()
                for frame_number, video_frame in enumerate(mmcv_video_frames):
                    if (num_skip_frames == 0) | (frame_number % num_skip_frames == 0):
                        # get tracking output
                        track_process_start = datetime.now()
                        
#                         track_results = inference_mot(tracking_model, video_frame, frame_id=frame_number)
#                         track_bboxes = track_results['track_bboxes'][0]
#                         track_results = [dict(bbox=x[1:], track_id=x[0]) for x in list(track_bboxes)]
                        
                        track_file = f'{TRACK_INFO_DIR}/{SESSION_KEYWORD}-front/{frame_number}.pb'
                        track_results = pickle.load(open(track_file,'rb'))[1]
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
                                face_embedding = None
                                if faces.shape[0] > 0:
                                    try:
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
                                    except:
                                        print(f"Error for face for body {body_index}, frame: {frame_number}")
                                        print(traceback.format_exc())
                                    frame_results[body_index].update({
                                        'face_embedding': face_embedding
                                    })
                        emb_process_end = datetime.now()

                        logger.info(
                            f"Frame: {frame_number} | embedding | {time_diff(emb_process_start, emb_process_end):.3f} secs")
                        
                        # output frame in tracking only dir
                        pickle.dump((frame_number, frame_results),
                                    open(f'{session_frames_output_dir}/{frame_number}.pb', 'wb'))
                pickle.dump((frame_number, frame_results), open(f'{session_frames_output_dir}/end.pb', 'wb'))
                time.sleep(5)
                torch.cuda.empty_cache()
