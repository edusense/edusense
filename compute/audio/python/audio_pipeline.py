# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.

from vggish_input import waveform_to_examples
import vggish_params
import numpy as np
from scipy.io import wavfile
import time 
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
parser.add_argument('--rpi_url', dest='rpi_url', type=str, nargs='?',
                    help='Remote Raspberry Pi URL') 
parser.add_argument('--backend_url', dest='backend_url', type=str, nargs='?',
                    help='EduSense backend')                     
parser.add_argument('--time_duration', dest='time_duration', type=int, nargs='?',
                    default=-1,help='Set the time duration for file to run')
parser.add_argument('--session_id', dest='session_id', type=str, nargs='?',
                    help='EduSense session ID')
parser.add_argument('--schema', dest='schema', type=str, nargs='?',
                    help='EduSense schema')
parser.add_argument('--ocr_time',dest='ocr_time',action='store_true',help="use OCR extracted timestamp")
parser.add_argument('--file_time',dest='file_time',action='store_true',help="use file_name timestamp")

args = parser.parse_args()


ip1 = args.front_url
ip2 = args.back_url
rpi_ip = args.rpi_url
rpi_port = 1243 # Just assuming that's the port I took
backend_url = args.backend_url
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
realtime=False

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
                	if len(b"".join(self.data[len(self.data)-2:])) == 1651 or len(self.msg) == 1651: break # Try breaking on >1651 to make it more robust
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
if rpi_ip is not None:
    rpi_proc = RPiReader(rpi_ip, rpi_port)
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
  date1,time1=gt.extract_time(ip1,args.ocr_time,args.file_time,log)
  log.write(f"{ip2} timestamp log\n")
  date2,time2=gt.extract_time(ip2,args.ocr_time,args.file_time,log)
  log.close()
  print(date1,str(time1))
  print(date2,str(time2))

print('........................')

if args.time_duration != -1:
  if not realtime:
      stop_time=time1+timedelta(seconds=args.time_duration)
  else:
      start_timer = time.perf_counter()

try:
    while(1):
        
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
        
        rpi_dic = rpi_proc.read()
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
                    'melFrequency': None,
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
                    'melFrequency': None,
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
        ## assuming audio is 1 fps
        frame_number += 1
        if not realtime:
           time1=time1+timedelta(seconds=1)
           time2=time2+timedelta(seconds=1)
    
        if False: # backend_url is not None:
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
                frame_url = 'https://' + args.backend_url + '/sessions/' + \
                    session_id + '/audio/frames/' + schema + '/raspi/'
                req = {'frames': [frames[2]]}
                resp = requests.post(frame_url, headers=headers, json=req)
                if (resp.status_code != 200 or 'success' not in resp.json().keys() or not resp.json()['success']):
                    raise RuntimeError(resp.text)
except Exception as e:
    raise RuntimeError("error occurred")


