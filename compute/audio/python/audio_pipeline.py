# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.

from vggish_input import waveform_to_examples
import vggish_params
import numpy as np
from scipy.io import wavfile
import time
import librosa
import subprocess
import os
import re
import sys
import argparse
from joblib import dump, load
import time
from datetime import date,datetime,timedelta
import json
import requests
import base64
import get_time as gt

frame_number = 0

def sampling_rate(video):
    specs=subprocess.Popen(['ffmpeg','-i',video,'-debug_ts'],stderr= subprocess.PIPE).stderr.read()
    specs=specs.decode('ascii')
    Mylist=specs.split(',')
    sampling=16000
    for ix in Mylist:
       if ix.find('Hz') != -1:
           result=re.findall('\d+', ix)
           sampling=int(result[0])
    return sampling


float_dtype = '>f4'

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
parser.add_argument('--time_duration', dest='time_duration', type=int, nargs='?',
                    default=-1,help='Set the time duration for file to run')
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
realtime=False

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
                                              '-'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            else:
                self.proc = subprocess.Popen(['ffmpeg',
                                              '-i', str(self.ip), '-nostats', '-loglevel', '0',
                                              '-vn', '-f', 's16le', '-acodec', 'pcm_s16le',
                                              '-'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)

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
rate1=sampling_rate(ip1)
rate2=sampling_rate(ip2)

## if log volume is mounted
try:
  log=open('/tmp/audio_log.txt','w')
except:
  log=open('audio_log.txt','w')

## check if real-time video
if 'rtsp' in ip1 or 'rtsp' in ip2:
     log.write("using RTSP\n")  
     realtime=True
     log.close()

else:
  ###extract starting time #####
  log.write(f"{ip1} timestamp log\n")
  date1,time1=gt.extract_time(ip1,log)
  print("Initial Date & Time",date1,time1)
  log.write(f"{ip2} timestamp log\n")
  date2,time2=gt.extract_time(ip2,log)
  log.close()
  print(date1,str(time1))
  print(date2,str(time2))

print('........................')

## temp code to dump audio info in file
student_audio_info = []
instructor_audio_info = []

if args.time_duration != -1:
  if not realtime:
      stop_time=time1+timedelta(seconds=args.time_duration)
  else:
      start_timer = time.perf_counter()

try:
    while(1):
        print("Ongoing Time", time1)
        if not realtime and args.time_duration != -1 and time1 > stop_time:
            print('timeout')
            sys.exit()

        if realtime and args.time_duration != -1 and time.perf_counter() - start_timer > args.time_duration:
            print('timeout')
            sys.exit()

        if realtime:
           timestamp1=datetime.utcnow().isoformat() + "Z"
        np_wav1 = ffmpeg_proc1.read(rate1)


        if realtime:
           timestamp2=datetime.utcnow().isoformat() + "Z"
        np_wav2 = ffmpeg_proc2.read(rate2)
    
        if np_wav1 is None or np_wav2 is None:
            break
        # print("Wav1:", len(np_wav1), np_wav1.mean(), np_wav1.max(), np_wav1.shape)

        ### New code for Mel Frequency Detection
        mel_spect1 = librosa.feature.melspectrogram(y=np_wav1, sr=rate1, n_fft=4096, hop_length=2048)
        mel_spect1 = librosa.power_to_db(mel_spect1, ref=1)
        mel_spect2 = librosa.feature.melspectrogram(y=np_wav2, sr=rate2, n_fft=4096, hop_length=2048)
        mel_spect2 = librosa.power_to_db(mel_spect2, ref=1)
        ### DON'T comment this out #####

        x1 = waveform_to_examples(np_wav1, rate1)
        x2 = waveform_to_examples(np_wav2, rate2)

        mel_feats1 = x1.astype(float_dtype)
        mel_feats2 = x2.astype(float_dtype)
            
        amp1 = max(abs(np_wav1))
        amp2 = max(abs(np_wav2))
        ##############################
        ## set the time stamps
        if not realtime:
           timestamp1=f"{date1}T{str(time1)}Z"
           timestamp2=f"{date2}T{str(time2)}Z"
        print(timestamp1)
        print(timestamp2)
        print(frame_number)
        print('........................................................................')
        # set the float point
        frames = [
            {
                'frameNumber': frame_number,
                'timestamp': timestamp1,
                'channel': 'instructor',
                'audio': {
                    'amplitude': amp1.tolist(),
                    'melFrequency': mel_spect1.tolist(),
                    'inference': {
                        'speech': {
                            'confidence': None,
                            'speaker': None
                        }
                    }
                },
                'SamplingRate': rate1
            }, {
                'frameNumber': frame_number,
                'timestamp': timestamp2,
                'channel': 'student',
                'audio': {
                    'amplitude': amp2.tolist(),
                    'melFrequency': mel_spect2.tolist(),
                    'inference': {
                        'speech': {
                            'confidence': None,
                            'speaker': None
                        }
                    }
                },
                'SamplingRate': rate2
            }
        ]
        ## assuming audio is 1 fps
        frame_number += 1
        instructor_audio_info.append(frames[0])
        student_audio_info.append(frames[1])

        ## Temp code: Write frames into json file
        if not realtime:
           time1=time1+timedelta(seconds=1)
           time2=time2+timedelta(seconds=1)
    
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
except Exception as e:
    raise RuntimeError("error occurred")

## temp code to dump audio info in file
DUMP_DIR = '/Users/ppatida2/Edusense/data/audio_spectrogram_experiments'
audio_student_filename = args.back_url.split("/")[-1].split(".")[0]
audio_instructor_filename = args.front_url.split("/")[-1].split(".")[0]
student_file_ptr = open(f'{DUMP_DIR}/{audio_student_filename}.json','w')
json.dump(student_audio_info, student_file_ptr)
student_file_ptr.close()
instructor_file_ptr = open(f'{DUMP_DIR}/{audio_instructor_filename}.json','w')
json.dump(instructor_audio_info, instructor_file_ptr)
instructor_file_ptr.close()
