# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.

from vggish_input import waveform_to_examples
from keras.models import load_model
import vggish_params
import tensorflow as tf
import numpy as np
from scipy.io import wavfile
import pyaudio
import time
import subprocess
import soundtransfer
import os
import sys
import inspect
import argparse
from joblib import dump, load
import time
import datetime
import json
import struct
import requests
import base64

frame_number = 0

context = soundtransfer.everything
trained_model = "models/example_model.hdf5"

labels = soundtransfer.labels
context = soundtransfer.everything

print("Using deep learning model: %s" % (trained_model))
model = load_model(trained_model)
graph = tf.compat.v1.get_default_graph()

label = dict()
for k in range(len(context)):
    label[k] = context[k]


def avg(l):
    return sum(l) / float(len(l))


# Variables
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = RATE  # 1024
float_dtype = '>f4'

clf = load('models/svm_speech.joblib')

##############################
# Parase Args
##############################
parser = argparse.ArgumentParser(
    description='EduSense audio pipeline')
parser.add_argument('--front_url', dest='front_url', type=str, nargs='?',
                    required=True, help='URL to rtsp front camera stream')
parser.add_argument('--back_url', dest='back_url', type=str, nargs='?',
                    required=True, help='URL to rtsp back camera stream')
parser.add_argument('--backend_url', dest='backend_url', type=str, nargs='?',
                    help='EduSense backend')
parser.add_argument('--session_id', dest='session_id', type=str, nargs='?',
                    help='EduSense session ID')
parser.add_argument('--schema', dest='schema', type=str, nargs='?',
                    help='EduSense schema')
args = parser.parse_args()

ip1 = args.front_url
ip2 = args.back_url
backend_url = args.backend_url
session_id = args.session_id
schema = 'edusense-audio' if args.schema is None else args.schema

class FFMpegReader:
    def __init__(self, ip):
        self.proc = None
        self.ip = ip

    def _procread(self, nbytes):
        if self.proc is None:
            if 'rtsp' in self.ip:
                self.proc = subprocess.Popen(['ffmpeg',
                                              '-i', str(self.ip), '-nostats', '-loglevel', '0',
                                              '-vn', '-f', 's16le', '-acodec', 'pcm_s16le',
                                              '-'], stdout=subprocess.PIPE)
            else:
                self.proc = subprocess.Popen(['ffmpeg',
                                              '-i', str(self.ip), '-nostats', '-loglevel', '0',
                                              '-vn', '-f', 's16le', '-acodec', 'pcm_s16le',
                                              '-'], stdout=subprocess.PIPE)
        return self.proc.stdout.read(nbytes)

    def read(self, nframes):
        out = bytearray()
        nbytes = nframes * 2

        if self.proc is not None and self.proc.poll() is not None:
            self.proc = None
            return None

        while len(out) < nbytes:
            chunk = self._procread(nbytes - len(out))
            if not chunk:
                try:
                    self.proc.kill()
                except:
                    pass
                self.proc = None
                continue
            out += chunk
        return np.frombuffer(out, dtype=np.int16) / 32768.0


ffmpeg_proc1 = FFMpegReader(ip1)
ffmpeg_proc2 = FFMpegReader(ip2)

try:
    while(1):
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        np_wav1 = ffmpeg_proc1.read(16000)
        np_wav2 = ffmpeg_proc2.read(16000)

        if np_wav1 is None or np_wav2 is None:
            break

        x1 = waveform_to_examples(np_wav1, RATE)
        x2 = waveform_to_examples(np_wav2, RATE)
        mel_feats1 = x1.astype(float_dtype)
        mel_feats2 = x2.astype(float_dtype)
        amp1 = max(abs(np_wav1))
        amp2 = max(abs(np_wav2))
        speech1 = 0
        speech2 = 0
        X = []
        X.append([max(np_wav1), max(np_wav2), max(np_wav1)/float(max(np_wav2))])
        prediction_teacher_vs_student = clf.predict(X)[0]
        predictions = []
        with graph.as_default():
            if x1.shape[0] != 0:
                x1 = x1.reshape(len(x1), 96, 64, 1)
                pred = model.predict(x1)
                predictions.append(pred)
            for prediction in predictions:
                n_items = prediction.shape[1]
                for k in range(n_items):
                    if label[k].capitalize() == 'Speech':
                        speech1 = prediction[0, k]
        predictions = []
        with graph.as_default():
            if x2.shape[0] != 0:
                x2 = x2.reshape(len(x2), 96, 64, 1)
                pred = model.predict(x2)
                predictions.append(pred)
            for prediction in predictions:
                n_items = prediction.shape[1]
                for k in range(n_items):
                    if label[k].capitalize() == 'Speech':
                        speech2 = prediction[0, k]

        mel_feats1 = list(
            map(lambda x: list(map(lambda y: round(y, 2), x)), mel_feats1.tolist()[0]))
        mel_feats2 = list(
            map(lambda x: list(map(lambda y: round(y, 2), x)), mel_feats2.tolist()[0]))

        # set the float point
        frames = [
            {
                'frameNumber': frame_number,
                'timestamp': timestamp,
                'channel': 'instructor',
                'audio': {
                    'amplitude': amp1.tolist(),
                    'melFrequency': mel_feats1,
                    'inference': {
                        'speech': {
                            'confidence': speech1.tolist(),
                            'speaker': prediction_teacher_vs_student
                        }
                    }
                }
            }, {
                'frameNumber': frame_number,
                'timestamp': timestamp,
                'channel': 'student',
                'audio': {
                    'amplitude': amp2.tolist(),
                    'melFrequency': mel_feats2,
                    'inference': {
                        'speech': {
                            'confidence': speech2.tolist(),
                            'speaker': prediction_teacher_vs_student
                        }
                    }
                }
            }
        ]

        frame_number += 1

        if backend_url is not None:
            app_username = os.getenv("APP_USERNAME", "")
            app_password = os.getenv("APP_PASSWORD", "")
            credential = '{}:{}'.format(app_username, app_password)
            headers = {
                'Authorization': ('Basic %s' % base64.standard_b64encode(credential.encode('ascii')).decode('ascii')),
                'Content-Type': 'application/json'}
            frame_url = 'https://' + args.backend_url + '/sessions/' + \
                session_id + '/audio/frames/' + schema + '/instructor/'
            req = {'frames': [frames[0]]}
            resp = requests.post(frame_url, headers=headers, json=req)
            if (resp.status_code != 200 or 'success' not in resp.json().keys() or not resp.json()['success']):
                raise RuntimeError(resp.text)
            frame_url = 'https://' + args.backend_url + '/sessions/' + \
                session_id + '/audio/frames/' + schema + '/student/'
            req = {'frames': [frames[1]]}
            resp = requests.post(frame_url, headers=headers, json=req)
            if (resp.status_code != 200 or 'success' not in resp.json().keys() or not resp.json()['success']):
                raise RuntimeError(resp.text)
except:
    raise RuntimeError("error occurred")
