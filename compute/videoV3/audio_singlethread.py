"""
This is main file to run Edusense audio pipeline with compute V3 on multiprocessing
"""
from configs.get_session_config import get_session_config
from utils_computev3 import get_logger, time_diff
from multiprocessing import Queue, Process
import moviepy.editor as mp
import whisper
import time
import torch
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

    speaker_feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained('microsoft/unispeech-sat-large-sv')
    speaker_verification_model = UniSpeechSatForXVector.from_pretrained('microsoft/unispeech-sat-large-sv')

    # audio files are decoded on the fly
    # inputs = speaker_feature_extractor(dataset[:2]["audio"]["array"] ,return_tensors="pt")
    inputs = speaker_feature_extractor([dataset[0]["audio"]["array"], dataset[1]["audio"]["array"]], padding=True, return_tensors="pt", sampling_rate=AUDIO_SR)
    embeddings = speaker_verification_model(**inputs).embeddings
    embeddings = torch.nn.functional.normalize(embeddings, dim=-1).cpu()

    # the resulting embeddings can be used for cosine similarity-based retrieval
    cosine_sim = torch.nn.CosineSimilarity(dim=-1)
    similarity = cosine_sim(embeddings[0], embeddings[1])
    threshold = 0.89  # the optimal threshold is dataset-dependent
    if similarity < threshold:
        print("Speakers are not the same!")
