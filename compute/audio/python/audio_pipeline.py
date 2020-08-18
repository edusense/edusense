# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.

# from vggish_input import waveform_to_examples
# from keras.models import load_model
# import vggish_params
# import tensorflow as tf
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
import socket
import pickle
import threading

frame_number = 0

# context = soundtransfer.everything
# trained_model = "models/example_model.hdf5"

# labels = soundtransfer.labels
# context = soundtransfer.everything

# print("Using deep learning model: %s" % (trained_model))
# model = load_model(trained_model)
# graph = tf.compat.v1.get_default_graph()

# label = dict()
# for k in range(len(context)):
#     label[k] = context[k]


def avg(l):
    return sum(l) / float(len(l))


# Variables
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = RATE  # 1024
float_dtype = '>f4'

# clf = load('models/svm_speech.joblib')

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
parser.add_argument('--rpi_url', dest='rpi_url', type=str, nargs='?',
                    help='Remote Raspberry Pi URL')                    
parser.add_argument('--session_id', dest='session_id', type=str, nargs='?',
                    help='EduSense session ID')
parser.add_argument('--schema', dest='schema', type=str, nargs='?',
                    help='EduSense schema')
parser.add_argument('--keyword', dest='keyword', type=str, nargs='?',
                    help='Keyword for Class Session') # Only for running the audio_pipeline by itself for RPi debugging
# parser.add_argument('--schema_rpi', dest='schema_rpi', type=str, nargs='?',
#                    help='Edusense schema for Raspberry Pi')
args = parser.parse_args()

ip1 = args.front_url
ip2 = args.back_url
rpi_ip = args.rpi_url
rpi_port = 1243 # Just assuming that's the port I took
backend_url = args.backend_url
print(backend_url)
print(args.keyword)
if args.session_id is None:
    app_username = os.getenv("APP_USERNAME", "")
    app_password = os.getenv("APP_PASSWORD", "")
    print(app_username)
    print(app_password)
    process = subprocess.Popen([
        'curl',
        '-X', 'POST',
        '-d', '{\"keyword\": \"%s\", \"data\":{\"from\":\"backfill\"}}' % args.keyword,
        '--header', 'Content-Type: application/json',
        '--basic', '-u', '%s:%s' % (app_username, app_password),
        'https://%s/sessions' % args.backend_url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    print(stderr)

    output = json.loads(stdout.decode('utf-8'))
    # print(output)
    success = output['success']
    session_id = output['session_id'].strip()
else:
    session_id = args.session_id
             
schema = 'edusense-audio' if args.schema is None else args.schema
# schema_rpi = 'edusense-audio-rpi' if args.schema_rpi is None else args.schema_rpi


print (session_id)

class RPiReader:
    def __init__(self, ip, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.s.connect((self.ip, self.port))

#         thread = threading.Thread(target = self.read, args=())
#         self.l = threading.Lock()
# #        thread.daemon = True
#         thread.start()

    def read(self):
        while True:
            # self.l.acquire()
            try:
                self.data = []
                while True:
                	self.msg = self.s.recv(2048)
#                	self.l.acquire()
                	self.data.append(self.msg)
                	# print(self.msg)
#                	self.l.release()
                	print(len(self.msg))
                	print(len(self.data))
                	if len(b"".join(self.data[len(self.data)-2:])) == 1651 or len(self.msg) == 1651: break
                self.ans = pickle.loads(b"".join(self.data))
                return self.ans
            except OSError:
                print ("Connection closed. Something may be wrong with the Pi")
                break
            # finally:
                # self.l.release()
    
    def fetch(self):
        # self.l.acquire()
        try:
            print("Data=", len(self.data))
            ans = pickle.loads(b"".join(self.data))
        finally:
            # self.l.release()
            return ans

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

print ('hello')
ffmpeg_proc1 = FFMpegReader(ip1)
ffmpeg_proc2 = FFMpegReader(ip2)
if rpi_ip is not None:
    rpi_proc = RPiReader(rpi_ip, rpi_port)

try:
    while(1):
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        print ("Hello", datetime.datetime.utcnow().isoformat() + "Z")
        np_wav1 = ffmpeg_proc1.read(16000)
        np_wav2 = ffmpeg_proc2.read(16000)
        print('Blweh', datetime.datetime.utcnow().isoformat() + "Z")
        # rpi_dic = rpi_proc.fetch()
        rpi_dic = rpi_proc.read()
        print("I'm here", datetime.datetime.utcnow().isoformat() + "Z")
        print(rpi_dic["SST"])
        if np_wav1 is None or np_wav2 is None:
            break

        # x1 = waveform_to_examples(np_wav1, RATE)
        # x2 = waveform_to_examples(np_wav2, RATE)
        # mel_feats1 = x1.astype(float_dtype)
        # mel_feats2 = x2.astype(float_dtype)
        amp1 = max(abs(np_wav1))
        amp2 = max(abs(np_wav2))
        # speech1 = 0
        # speech2 = 0
        # X = []
        # X.append([max(np_wav1), max(np_wav2), max(np_wav1)/float(max(np_wav2))])
        # prediction_teacher_vs_student = clf.predict(X)[0]
        # predictions = []
        # with graph.as_default():
        #     if x1.shape[0] != 0:
        #         x1 = x1.reshape(len(x1), 96, 64, 1)
        #         pred = model.predict(x1)
        #         predictions.append(pred)
        #     for prediction in predictions:
        #         n_items = prediction.shape[1]
        #         for k in range(n_items):
        #             if label[k].capitalize() == 'Speech':
        #                 speech1 = prediction[0, k]
        # predictions = []
        # with graph.as_default():
        #     if x2.shape[0] != 0:
        #         x2 = x2.reshape(len(x2), 96, 64, 1)
        #         pred = model.predict(x2)
        #         predictions.append(pred)
        #     for prediction in predictions:
        #         n_items = prediction.shape[1]
        #         for k in range(n_items):
        #             if label[k].capitalize() == 'Speech':
        #                 speech2 = prediction[0, k]

        # mel_feats1 = list(
        #     map(lambda x: list(map(lambda y: round(y, 2), x)), mel_feats1.tolist()[0]))
        # mel_feats2 = list(
        #     map(lambda x: list(map(lambda y: round(y, 2), x)), mel_feats2.tolist()[0]))

        # set the float point
        frames = [
            {
                'frameNumber': frame_number,
                'timestamp': timestamp,
                'channel': 'instructor',
                'audio': {
                    'amplitude': amp1.tolist(),
                    'melFrequency': None,
                    'inference': {
                        'speech': {
                            'confidence': None,
                            'speaker': None
                        }
                    }
                }
            }, {
                'frameNumber': frame_number,
                'timestamp': timestamp,
                'channel': 'student',
                'audio': {
                    'amplitude': amp2.tolist(),
                    'melFrequency': None, # mel_feats2,
                    'inference': {
                        'speech': {
                            'confidence': None, # speech2.tolist(),
                            'speaker': None # prediction_teacher_vs_student
                        }
                    }
                }
            }
        ]
        if rpi_ip is not None:
            rpi_json = [
                {
                'frameNumber': frame_number,
                'timestamp': timestamp,
                'channel': 'raspi',
                'audio': {
                   'SSL': rpi_dic["SSL"],
                   'FFT': rpi_dic["FFT"],
                   'SST': rpi_dic["SST"]
                  }
                }
            ]
            frames.append(rpi_json[0])

        frame_number += 1

        if False: # backend_url is not None:
            print("Going to post", datetime.datetime.utcnow().isoformat() + "Z")
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
            if rpi_ip is not None:
                print ("Posting the RPi", datetime.datetime.utcnow().isoformat() + "Z")
                frame_url = 'https://' + args.backend_url + '/sessions/' + \
                    session_id + '/audio/frames/' + schema + '/raspi/'
                req = {'frames': [frames[2]]}
                resp = requests.post(frame_url, headers=headers, json=req)
                print(resp.json().keys(), frame_number, datetime.datetime.utcnow().isoformat() + "Z")
                if (resp.status_code != 200 or 'success' not in resp.json().keys() or not resp.json()['success']):
                    raise RuntimeError(resp.text)
except:
    raise RuntimeError("error occurred")
