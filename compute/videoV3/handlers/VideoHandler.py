'''
Handler to process video into frames and passing to tracking processes
'''

import mmcv
import time
from queue import Empty as EmptyQueueException


def run_video_handler(video_input_queue, frame_output_queue, session_config, logger, loop_wait_time=0.5):
    # read video file
    class_video_file = f'{session_config["session_dir"]}/{session_config["session_keyword"]}'
    mmcv_video_frames = mmcv.VideoReader(class_video_file)
    fps = mmcv_video_frames.fps
    h, w, _ = mmcv_video_frames[0].shape

    logger.info("reading frames from video")

    session_config.update({
        'frame_width': w,
        'frame_height': h,
        'fps': fps,
    })
    for frame_number, video_frame in enumerate(mmcv_video_frames):
        frame_output_queue.put((frame_number, video_frame))
        logger.info(f"pushed frame {frame_number}")
        time.sleep(loop_wait_time)

    frame_output_queue.put((frame_number, None))
    return None
