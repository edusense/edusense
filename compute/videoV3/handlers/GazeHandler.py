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


def run_gaze_handler(gaze_input_queue, gaze_output_queue, session_config, logger_name):
    logger = get_logger(logger_name)
    # init gaze model
    gaze_model = GazeInference(device=session_config['device'])

    while True:
        wait_start = datetime.now()
        try:
            frame_number, video_frame, face_results = gaze_input_queue.get(timeout=0.1)
        except EmptyQueueException:
            time.sleep(0.5)
            continue
        wait_end = datetime.now()
        if video_frame is None:
            logger.info("Received none frame from input queue, exiting tracking handler.")
            gaze_output_queue.put((frame_number, 'gaze', None))
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

            gaze_output_queue.put((frame_number, 'gaze', gaze_results))

        process_end = datetime.now()
        logger.info(
            f"Frame: {frame_number}, {time_diff(wait_start, wait_end):.3f} secs | {time_diff(process_start, process_end):.3f} secs")

    return None
