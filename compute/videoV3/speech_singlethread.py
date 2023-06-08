import os.path

import whisperx
import whisper
import moviepy.editor as mp
import time
import librosa
import torch
from transformers import Wav2Vec2FeatureExtractor, UniSpeechSatForXVector
from copy import deepcopy
import pickle
import glob
from utils_computev3 import get_logger, time_diff
import traceback
import sys

# conda activate edusense && export PYTHONPATH="${PYTHONPATH}:/home/prasoon/video_analysis/edusenseV2compute/compute/videoV3/"

SOURCE_DIR = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV3'
VIDEO_DIR = f"/mnt/ci-nas-classes/classinsight/{sys.argv[1]}/video_backup"
# SESSION_KEYWORD = 'classinsight-cmu_79388A_ghc_4301_201910031826'
OUT_DIR = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV3/cache/audio'
os.makedirs(OUT_DIR,exist_ok=True)
DEVICE = f"cuda:{sys.argv[2]}"
WHISPER_MODEL = 'medium'
BLOCK_SIZE_IN_SECS = 300
AUDIO_SR = 16000
MIN_SEGMENT_TIME_IN_SECS = 1
logger = get_logger(f"edusense_audio_pipeline_{VIDEO_DIR.split('/')[-2]}")


session_dirs = glob.glob(f'{VIDEO_DIR}/*')
logger.info(f"Got {len(session_dirs)} sessions from {VIDEO_DIR}")
for session_dir in session_dirs:
    SESSION_KEYWORD = session_dir.split("/")[-1]
    logger.info(f"processing for session {SESSION_KEYWORD}")
    t_start_transcription = time.time()
    # create mp3 if not present
    for camera_view in ['front','back']:
        logger.info(f"Start Audio Pipeline for {camera_view} Camera")
        session_video_file = f'{session_dir}/{SESSION_KEYWORD}-{camera_view}.avi'
        OUT_FILE = f'{OUT_DIR}/{SESSION_KEYWORD}-{camera_view}.pb'
        session_video_file = f'{session_dir}/{SESSION_KEYWORD}-{camera_view}.avi'
        if os.path.exists(OUT_FILE):
            logger.info(f"Output file {OUT_FILE} exists for camera {session_video_file}, Skipping..")
            continue

        if not os.path.exists(session_video_file):
            logger.info(f"camera video file {session_video_file} does not exist. Skipping...")
            continue

        session_audio_file = f'/tmp/{SESSION_KEYWORD}-{camera_view}.mp3'
        # session_audio_file = f'/tmp/first-10-min_5fps.mp3'

        if not os.path.exists(session_audio_file):
            logger.info("Creating session audio file")
            start_time = time.time()
            try:
                session_video_clip = mp.VideoFileClip(session_video_file)
                session_video_clip.audio.write_audiofile(session_audio_file)
                end_time = time.time()
                logger.info(f"Got audio clip in {end_time - start_time:3f}")
            except OSError:
                logger.error(traceback.format_exc())
                logger.info(f"Skipping camera {session_video_file}...")
                continue

        # transcribe with original whisper
        try:
            model = whisper.load_model(WHISPER_MODEL, DEVICE)
        except torch.cuda.OutOfMemoryError:
            logger.error("Cuda memory not emptied in clean manner, removing again...")
            torch.cuda.empty_cache()
            time.sleep(5)
            model = whisper.load_model(WHISPER_MODEL, DEVICE)


        try:
            start_time = time.time()
            result = model.transcribe(session_audio_file, language='en')
            end_time = time.time()
            logger.info(f"Time taken for transcription {end_time - start_time:3f} secs...")  # before alignment
        except:
            logger.info("Issue with transcription from original model")
            logger.info(traceback.format_exc())

        del model
        time.sleep(5)
        torch.cuda.empty_cache()

        start_time = time.time()
        # load alignment model and metadata
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=DEVICE)

        try:
            # align whisper output
            result_aligned = whisperx.align(result["segments"], model_a, metadata, session_audio_file, DEVICE)
        except:
            logger.info("Issue with aligning model outputs")
            logger.info(traceback.format_exc())
            result_aligned = None

        end_time = time.time()
        logger.info(f"Time taken for alignment {end_time - start_time:3f} secs...")  # before alignment

        del model_a, metadata, result
        torch.cuda.empty_cache()

        if result_aligned is None:
            logger.info("Skipping speaker verification submodule...")
            if os.path.exists(session_audio_file):
                os.remove(session_audio_file)
                logger.info(f"Removed {session_audio_file}")
            continue

        start_time = time.time()
        # model and feature extractor for speaker identification
        speaker_feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained('microsoft/unispeech-sat-large-sv')
        speaker_verification_model = UniSpeechSatForXVector.from_pretrained('microsoft/unispeech-sat-large-sv').to(DEVICE)

        classroom_audio, sampling_rate = librosa.load(session_audio_file)
        classroom_audio = librosa.resample(classroom_audio, orig_sr=sampling_rate, target_sr=AUDIO_SR)

        for idx, segment in enumerate(result_aligned["segments"]):
            seg_start, seg_end = segment["start"], segment["end"]
            try:
                logger.info(f'{idx} | {seg_start}-->{seg_end} | {segment["text"]}')
            except:
                logger.info(f'Unable to logger.info segment')
            if segment["end"] - segment["start"] <= MIN_SEGMENT_TIME_IN_SECS:
                logger.info("Segment too short for speaker embedding, skipping")
                continue
            try:
                segment_speech = classroom_audio[int(seg_start * AUDIO_SR):int(seg_end * AUDIO_SR)]
                segment_speech_featurized = speaker_feature_extractor([segment_speech], padding=True, return_tensors="pt",
                                                                      sampling_rate=AUDIO_SR).to(DEVICE)
                embeddings = speaker_verification_model(**segment_speech_featurized).embeddings
                embeddings = torch.nn.functional.normalize(embeddings, dim=-1).cpu().detach().numpy().squeeze()
                result_aligned["segments"][idx]['speaker_embedding'] = deepcopy(embeddings)
                del embeddings, segment_speech_featurized
                torch.cuda.empty_cache()
            except:
                logger.info("Unable to process segment for speech")


        pickle.dump(result_aligned, open(OUT_FILE, 'wb'))
        end_time = time.time()
        del speaker_feature_extractor, speaker_verification_model
        torch.cuda.empty_cache()

        logger.info(f"Time taken for speaker embedding {end_time - start_time:3f} secs...")  # before alignment
        t_end_transcription = time.time()
        logger.info(f"Time taken end to end for {camera_view}: {t_end_transcription - t_start_transcription:3f} secs...")  # before alignment
        if os.path.exists(session_audio_file):
            os.remove(session_audio_file)
            logger.info(f"Removed {session_audio_file}")


'''
- Attribution for ephimeral consent in classroom.
    - privacy and utility are at different ends. 
    - Dialing back and forward based on consent level.

'''
