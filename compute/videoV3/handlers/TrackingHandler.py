'''
Handler to process video frames and return tracking handler
'''

import numpy as np
from mmtrack.apis import inference_mot, init_model as init_tracking_model
from datetime import datetime
from utils_computev3 import time_diff, get_logger
import time
from queue import Empty as EmptyQueueException


def run_tracking_handler(frame_input_queue, pose_queue, face_queue, session_config, logger_name):
    logger = get_logger(logger_name)
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
