"""
This is main file to run Edusense audio pipeline with compute V3 on multiprocessing
"""
from configs.get_session_config import get_session_config
from utils_computev3 import get_logger, time_diff
from multiprocessing import Queue, Process
import handlers
import torch
import moviepy.editor as mp
import whisper
import time
from transformers import Wav2Vec2FeatureExtractor, UniSpeechSatForXVector
from datasets import load_dataset

SOURCE_DIR = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV3'
SESSION_DIR = '/home/prasoon/video_analysis/mmtracking/'
SESSION_KEYWORD = 'first-10-min_5fps.mp4'
OUT_DIR = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV3/cache'
DEVICE = 'cuda:1'
BLOCK_SIZE_IN_SECS=300
AUDIO_SR = 16000

if __name__ == '__main__':

    dataset = load_dataset("hf-internal-testing/librispeech_asr_demo", "clean", split="validation")

    feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained('microsoft/unispeech-sat-large-sv')
    model = UniSpeechSatForXVector.from_pretrained('microsoft/unispeech-sat-large-sv')

    # audio files are decoded on the fly
    inputs = feature_extractor(dataset[:2]["audio"]["array"], return_tensors="pt")
    embeddings = model(**inputs).embeddings
    embeddings = torch.nn.functional.normalize(embeddings, dim=-1).cpu()

    # the resulting embeddings can be used for cosine similarity-based retrieval
    cosine_sim = torch.nn.CosineSimilarity(dim=-1)
    similarity = cosine_sim(embeddings[0], embeddings[1])
    threshold = 0.89  # the optimal threshold is dataset-dependent
    if similarity < threshold:
        print("Speakers are not the same!")

    torch.multiprocessing.set_start_method('spawn')
    # TODO: Setup Parser for command line runs and docker runs
    session_config = get_session_config(SOURCE_DIR, SESSION_DIR, SESSION_KEYWORD, OUT_DIR, DEVICE)

    # setup logger
    logger = get_logger("edusense_audio_pipeline")

    # Setup multiprocessing queues <input>_<output>_queue

    audio_speech_queue = Queue()
    speech_speaker_queue = Queue()
    video_output_queue = Queue()
    audio_output_queue = Queue()

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

