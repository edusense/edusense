"""
This is main file to run Edusense pipeline with compute V3 on multiprocessing
"""
from configs.get_session_config import get_session_config
from utils_computev3 import get_logger, time_diff
from multiprocessing import Queue, Process
import handlers
import torch
import time

SOURCE_DIR = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV3'
SESSION_DIR = '/mnt/ci-nas-classes/classinsight/2019F/video_backup'
SESSION_KEYWORD = 'classinsight-cmu_79388A_ghc_4301_201910031826'
SESSION_CAMERA = 'front'
# SOURCE_DIR = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV3'
# SESSION_DIR = '/home/prasoon/video_analysis/mmtracking/'
# SESSION_KEYWORD = 'first-10-min_5fps.mp4'
OUT_DIR = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV3/cache'
DEVICE = 'cuda:0'
NUM_FACE_DETECTION_HANDLERS = 1
TARGET_FPS = 3
START_FRAME_NUMBER = 0 # used for debug purposes only
FRAME_INTERVAL_IN_SEC =  0.5
MAX_QUEUE_SIZE=3000

if __name__ == '__main__':
    torch.multiprocessing.set_start_method('spawn')
    # TODO: Setup Parser for command line runs and docker runs
    session_config = get_session_config(SOURCE_DIR, SESSION_DIR, SESSION_KEYWORD, SESSION_CAMERA, OUT_DIR, DEVICE, TARGET_FPS, start_frame_number = START_FRAME_NUMBER, frame_interval=FRAME_INTERVAL_IN_SEC)
    session_config['num_face_detection_handlers'] = NUM_FACE_DETECTION_HANDLERS
    # setup logger
    logger = get_logger("edusense_pipeline")

    # Setup multiprocessing queues <input>_<output>_queue

    video_tracking_queue = Queue(maxsize=MAX_QUEUE_SIZE)
    tracking_pose_queue = Queue(maxsize=MAX_QUEUE_SIZE)
    tracking_face_queue = Queue(maxsize=MAX_QUEUE_SIZE)

    pose_output_queue = Queue(maxsize=MAX_QUEUE_SIZE)
    face_gaze_queue = Queue(maxsize=MAX_QUEUE_SIZE)
    face_embedding_queue = Queue(maxsize=MAX_QUEUE_SIZE)
    video_output_queue = Queue(maxsize=MAX_QUEUE_SIZE)

    # initialize output handler
    output_handler = Process(target=handlers.run_output_handler,
                               args=(video_output_queue, session_config,"output"))
    output_handler.start()

    # initialize support handlers
    tracking_handler = Process(target=handlers.run_tracking_handler,
                               args=(video_tracking_queue, tracking_pose_queue, tracking_face_queue, session_config, "tracker"))
    tracking_handler.start()

    pose_handler = Process(target=handlers.run_pose_handler,
                               args=(tracking_pose_queue, video_output_queue, session_config, "pose"))
    pose_handler.start()

    face_detection_handlers = [None]*NUM_FACE_DETECTION_HANDLERS
    for i in range(NUM_FACE_DETECTION_HANDLERS):
        face_detection_handlers[i] = Process(target=handlers.run_face_handler,
                                   args=(tracking_face_queue, face_gaze_queue, face_embedding_queue, session_config, "face_detection"))
        face_detection_handlers[i].start()

    gaze_handler = Process(target=handlers.run_gaze_handler,
                               args=(face_gaze_queue, video_output_queue, session_config, "gaze"))
    gaze_handler.start()

    face_embedding_handler = Process(target=handlers.run_face_embedding_handler,
                               args=(face_embedding_queue, video_output_queue, session_config, "face_embedding"))
    face_embedding_handler.start()

    # start video and audio handlers
    video_handler = Process(target=handlers.run_video_handler,
                               args=(None, video_tracking_queue, session_config, logger))
    video_handler.start()

    # start observing output queue


    video_handler.join()
    tracking_handler.join()
    pose_handler.join()
    for i in range(NUM_FACE_DETECTION_HANDLERS):
        face_detection_handlers[i].join()
    gaze_handler.join()
    face_embedding_handler.join()

