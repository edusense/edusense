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
from queue import Empty as EmptyQueueException
from concurrent.futures import ThreadPoolExecutor

def run_face_handler(face_input_queue, gaze_input_queue, face_embedding_input_queue, session_config, logger_name):
    logger = get_logger(logger_name)
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
