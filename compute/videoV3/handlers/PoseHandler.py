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

def run_pose_handler(pose_input_queue, pose_output_queue, session_config, logger_name):
    logger = get_logger(logger_name)
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
