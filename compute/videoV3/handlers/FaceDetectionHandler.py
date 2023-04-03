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


def run_face_handler(face_input_queue, gaze_input_queue, face_embedding_input_queue, session_config, logger_name):
    logger = get_logger(logger_name)
    # init face boundingbox model
    retinaface = RetinaFaceInference(device=torch.device(session_config['device']))
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
            face_results = deepcopy(track_results)
            body_count = len(face_results)
            for body_index, tracking_info in enumerate(track_results):
                if type(tracking_info) == dict:
                    body_bbox = tracking_info['bbox']
                    X_TL, Y_TL, X_BR, Y_BR = body_bbox[:4].astype(int)
                    body_frame = video_frame[Y_TL:Y_BR, X_TL:X_BR, :]
                    faces, _ = retinaface.run(body_frame, frame_debug=None)
                    face_results[body_index].update({
                        'face':faces
                    })

            gaze_input_queue.put((frame_number, video_frame, face_results))
            face_embedding_input_queue.put((frame_number, video_frame, face_results))
            success = True

        process_end = datetime.now()
        logger.info(
            f"Frame: {frame_number}, {time_diff(wait_start, wait_end):.3f} secs | {time_diff(process_start, process_end):.3f} secs [{body_count}]")

    return None
