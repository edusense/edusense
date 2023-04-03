'''
Handler to process output information
'''

import numpy as np
from datetime import datetime
from utils_computev3 import time_diff, get_logger
from copy import deepcopy
import time
from queue import Empty as EmptyQueueException
import pickle


def run_output_handler(output_queue, session_config, logger_name):
    logger = get_logger(logger_name)
    # init gaze, embedding and pose dictionaries
    session_info = {
        'gaze': [],
        'face_embedding': [],
        'pose': []
    }
    session_output_file_prefix = f'{session_config["OUT_DIR"]}/{session_config["KEYWORD"].split(".mp4")[0]}'
    while True:
        try:
            frame_number, frame_type, frame_data = output_queue.get(timeout=0.1)
        except EmptyQueueException:
            time.sleep(0.5)
            continue
        if frame_type not in session_info.keys():
            logger.info(f"Frame Type {frame_type} is not supported..")
            continue
        session_info[frame_type].append((frame_number, frame_data))

        if (frame_number%100==0) & (frame_type=='face_embedding'):
            pickle.dump(session_info, open(f'{session_output_file_prefix}_{frame_number}.pb','wb'))
            logger.info(f"Stored frames till {frame_number}")


    return None
