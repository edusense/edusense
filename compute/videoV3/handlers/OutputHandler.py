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
    session_out_dir, session_keyword, session_camera = session_config["output_dir"], session_config["session_keyword"], \
                                                   session_config["session_camera"]
    session_output_file_prefix = f'{session_out_dir}/{session_keyword}-{session_camera}'
    final_packet_received = {
        'gaze': False,
        'face_embedding': False,
        'pose': False
    }
    start_time = time.time()
    while True:
        try:
            frame_number, frame_type, frame_data = output_queue.get(timeout=0.1)
        except EmptyQueueException:
            time.sleep(0.5)
            continue
        if frame_type not in session_info.keys():
            logger.info(f"Frame Type {frame_type} is not supported..")
            continue
        if frame_data is None:
            final_packet_received[frame_type] = True
            if (final_packet_received['gaze']) & (final_packet_received['pose']) & (
            final_packet_received['face_embedding']):
                logger.info("All frames received, closing output handler...")
                pickle.dump(session_info, open(f'{session_output_file_prefix}_all.pb', 'wb'))
                break
        else:
            session_info[frame_type].append((frame_number, frame_data))
        if (frame_number % 1000 == 0) & (frame_type == 'face_embedding'):
            pickle.dump(session_info, open(f'{session_output_file_prefix}_{frame_number}.pb', 'wb'))
            logger.info(f"Stored frames till {frame_number} in {time.time() - start_time:3f} secs..")
            start_time = time.time()

    return None
