'''
Handler to process video into frames and passing to tracking processes
'''

import mmcv
import time
from queue import Empty as EmptyQueueException


def run_video_handler(video_input_queue, frame_output_queue, session_config, logger):
    # read video file
    session_dir, session_keyword, session_camera =session_config["session_dir"], session_config["session_keyword"], session_config["session_camera"]
    class_video_file = f'{session_dir}/{session_keyword}/{session_keyword}-{session_camera}.avi'
    mmcv_video_frames = mmcv.VideoReader(class_video_file)
    video_fps = mmcv_video_frames.fps
    target_fps = session_config['target_fps']
    start_frame_number, frame_interval = session_config['start_frame_number'], session_config['frame_interval']

    h, w, _ = mmcv_video_frames[0].shape

    logger.info("reading frames from video")

    session_config.update({
        'frame_width': w,
        'frame_height': h,
        'fps': target_fps,
    })
    num_skip_frames = int(video_fps / target_fps)
    logger.info(f"Target FPS: {target_fps}, Video FPS: {video_fps}, Num Skip Frames: {num_skip_frames}")

    processing_started = False
    for frame_number, video_frame in enumerate(mmcv_video_frames):
        if frame_number < start_frame_number:
            continue
        elif not processing_started:
            logger.warning(f"Skipped {frame_number} frames, make sure you are running in debug mode...")
            processing_started = True

        if (num_skip_frames == 0) | (frame_number % num_skip_frames == 0):
            frame_output_queue.put((frame_number, video_frame))
            logger.info(f"pushed frame {frame_number}")
            if frame_interval >0.:
                time.sleep(frame_interval)

    frame_output_queue.put((frame_number, None))
    return None
