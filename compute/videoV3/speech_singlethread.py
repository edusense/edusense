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

t_start_transcription = time.time()
SOURCE_DIR = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV3'
SESSION_DIR = '/mnt/ci-nas-classes/classinsight/2019F/video_backup'
SESSION_KEYWORD = 'classinsight-cmu_79388A_ghc_4301_201910031826'
OUT_DIR = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV3/cache'
DEVICE = 'cuda:0'
WHISPER_MODEL = 'large-v2'
BLOCK_SIZE_IN_SECS = 300
AUDIO_SR = 16000
MIN_SEGMENT_TIME_IN_SECS = 1

# create mp3 if not present
for camera_view in ['back']:
    print(f"Start Audio Pipeline for {camera_view} Camera")
    session_video_file = f'{SESSION_DIR}/{SESSION_KEYWORD}/{SESSION_KEYWORD}-{camera_view}.avi'
    session_audio_file = f'/tmp/{SESSION_KEYWORD}-{camera_view}.mp3'
    # session_audio_file = f'/tmp/first-10-min_5fps.mp3'

    if not os.path.exists(session_audio_file):
        print("Creating session audio file")
        start_time = time.time()
        session_video_clip = mp.VideoFileClip(session_video_file)
        session_video_clip.audio.write_audiofile(session_audio_file)
        end_time = time.time()
        print(f"Got audio clip in {end_time - start_time:3f}")

    # transcribe with original whisper
    model = whisper.load_model(WHISPER_MODEL, DEVICE)
    start_time = time.time()
    result = model.transcribe(session_audio_file, language='en')
    end_time = time.time()
    print(f"Time taken for transcription {end_time - start_time:3f} secs...")  # before alignment

    del model
    torch.cuda.empty_cache()

    start_time = time.time()
    # load alignment model and metadata
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=DEVICE)

    # align whisper output
    result_aligned = whisperx.align(result["segments"], model_a, metadata, session_audio_file, DEVICE)
    end_time = time.time()
    print(f"Time taken for alignment {end_time - start_time:3f} secs...")  # before alignment

    del model_a, metadata, result
    torch.cuda.empty_cache()

    start_time = time.time()
    # model and feature extractor for speaker identification
    speaker_feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained('microsoft/unispeech-sat-large-sv')
    speaker_verification_model = UniSpeechSatForXVector.from_pretrained('microsoft/unispeech-sat-large-sv').to(DEVICE)

    classroom_audio, sampling_rate = librosa.load(session_audio_file)
    classroom_audio = librosa.resample(classroom_audio, orig_sr=sampling_rate, target_sr=AUDIO_SR)

    for idx, segment in enumerate(result_aligned["segments"]):
        seg_start, seg_end = segment["start"], segment["end"]
        try:
            print(f'{idx} | {seg_start}-->{seg_end} | {segment["text"]}')
        except:
            print(f'Unable to print segment')
        if segment["end"] - segment["start"] <= MIN_SEGMENT_TIME_IN_SECS:
            print("Segment too short for speaker embedding, skipping")
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
            print("Unable to process segment for speech")

    OUT_FILE = f'{OUT_DIR}/{SESSION_KEYWORD}-{camera_view}.pb'
    pickle.dump(result_aligned, open(OUT_FILE, 'wb'))
    end_time = time.time()
    del speaker_feature_extractor, speaker_verification_model
    torch.cuda.empty_cache()

    print(f"Time taken for speaker embedding {end_time - start_time:3f} secs...")  # before alignment
    t_end_transcription = time.time()
    print(f"Time taken end to end for {camera_view}: {t_end_transcription - t_start_transcription:3f} secs...")  # before alignment

#
# # load audio and pad/trim it to fit 30 seconds
# model = whisper.load_model("large-v2")
# audio = whisper.load_audio(session_audio_file)
# audio = whisper.pad_or_trim(audio)
#
# # make log-Mel spectrogram and move to the same device as the model
# mel = whisper.log_mel_spectrogram(audio).to(model.device)
#
# # detect the spoken language
# _, probs = model.detect_language(mel)
# print(f"Detected language: {max(probs, key=probs.get)}")
#
# # decode the audio
# options = whisper.DecodingOptions()
# result = whisper.decode(model, mel, options)
#
# subtitle_result = model.transcribe(session_audio_file, language='en',verbose=True)
# # print the recognized text
# print(result.text)

'''
- Attribution for ephimeral consent in classroom.
    - privacy and utility are at different ends. 
    - Dialing back and forward based on consent level.

'''