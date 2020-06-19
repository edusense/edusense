#!/usr/bin/python3

import argparse
import json
import os
import sys
import subprocess
import tempfile
import time
from threading import Timer

def kill_all_containers(containers):
    print('killing all containers')

    process = subprocess.Popen(['docker', 'container', 'kill'] + containers,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    killed_container_ids = stdout.decode('utf-8').split()
    for c in killed_container_ids:
        print('killed container', c)
    print(stderr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='EduSense deploy video')
    parser.add_argument('--front_video', dest='front_video', type=str, nargs='?',
        required=True, help='video file for front ip camera')
    parser.add_argument('--developer', dest='dev', type=str, nargs='?',
        required=True, help='enter developer tag name')
    parser.add_argument('--back_video', dest='back_video', type=str, nargs='?',
        required=True, help='video for back ip camera')
    parser.add_argument('--keyword', dest='keyword', type=str, nargs='?',
        required=True, help='Keyword for class session')
    parser.add_argument('--backend_url', dest='backend_url', type=str, nargs='?',
        required=True, help='EduSense backend address')
    parser.add_argument('--front_num_gpu_start', dest='front_num_gpu_start', type=int, nargs='?',
        required=True, help='GPU start index for front camera processing')
    parser.add_argument('--front_num_gpu', dest='front_num_gpu', type=int, nargs='?',
        required=True, help='number of GPUs for front camera processing')
    parser.add_argument('--back_num_gpu_start', dest='back_num_gpu_start', type=int, nargs='?',
        required=True, help='GPU start index for back camera processing')
    parser.add_argument('--back_num_gpu', dest='back_num_gpu', type=int, nargs='?',
        required=True, help='number of GPUs for back camera processing')
    parser.add_argument('--time_duration', dest='time_duration', type=int, nargs='?',
        required=True, help='time duration for executing CI')
    parser.add_argument('--video_schema', dest='video_schema', type=str, nargs='?',
        required=True, help='video schema for CI')
    parser.add_argument('--audio_schema', dest='audio_schema', type=str, nargs='?',
        required=True, help='audio schema for CI')
    parser.add_argument('--log_dir', dest='log_dir' ,type=str, nargs='?',
            help='get the logs in a directory')
    parser.add_argument('--video_dir', dest='video_dir', type=str, nargs='?',
        required=True, help='directory for video')
    parser.add_argument('--process_real_time', dest='process_real_time',
                        action='store_true', help='if set, skip frames to keep'
                        ' realtime')
    parser.add_argument('--tensorflow_gpu', dest='tensorflow_gpu', type=str, nargs='?',
                        default='-1', help='tensorflow gpus')
    args = parser.parse_args()

    uid = os.getuid()
    gid = os.getgid()
    app_username = os.getenv("APP_USERNAME", "")
    app_password = os.getenv("APP_PASSWORD", "")

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
    try:
      output = json.loads(stdout.decode('utf-8'))
      success = output['success']
      session_id = output['session_id'].strip()
    except:
        print("Unable to create a session")
        print("check APP username and password")
        sys.exit(1)
    
    print('created session', session_id)

    real_time_flag = ['--process_real_time'] if args.process_real_time \
                    else []
    print(args.log_dir)
    # create temp directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        if args.log_dir == None:
            args.log_dir=tmp_dir
        print('create temporary directory', tmp_dir)
        process = subprocess.Popen([
            'nvidia-docker', 'run', '-d',
            '-e', 'LOCAL_USER_ID=%s' % uid,
            '-e', 'CUDA_VISIBLE_DEVICES=%s' % args.tensorflow_gpu,
            '-e', 'APP_USERNAME=%s' % app_username,
            '-e', 'APP_PASSWORD=%s' % app_password,
            '-v', '%s:/app/source' %args.video_dir,
            '-v', '%s:/tmp' % args.log_dir,
            '--rm',
            'edusense/video:'+args.dev,
            '--video',os.path.join('/app', 'source', args.front_video),
            '--video_sock', '/tmp/unix.front.sock',
            '--backend_url', args.backend_url,
            '--session_id', session_id,
            '--schema', args.video_schema,
            '--use_unix_socket',
            '--keep_frame_number',
            '--process_gaze',
            '--profile',
            '--time_duration', str(args.time_duration + 60) if args.time_duration >= 0 else '-1'] + real_time_flag,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        front_video_container_id = stdout.decode('utf-8').strip()

        print('created front video container', front_video_container_id)

        process = subprocess.Popen([
            'docker', 'run', '-d',
            '-e', 'LOCAL_USER_ID=%s' % uid,
            '-e', 'APP_USERNAME=%s' % app_username,
            '-e', 'APP_PASSWORD=%s' % app_password,
            '-v', '%s:/tmp' % args.log_dir,
            '-v', '%s:/app/source' %args.video_dir,
            '--rm',
            'edusense/video:'+args.dev,
            '--video',os.path.join('/app', 'source', args.back_video),
            '--video_sock', '/tmp/unix.back.sock',
            '--backend_url', args.backend_url,
            '--session_id', session_id,
            '--schema', args.video_schema,
            '--use_unix_socket',
            '--keep_frame_number',
            '--time_duration', str(args.time_duration + 60) if args.time_duration >= 0 else '-1',
            '--process_gaze',
            '--profile',
            '--instructor'] + real_time_flag,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        back_video_container_id = stdout.decode('utf-8').strip()

        print('created back video container', back_video_container_id)

        time.sleep(30)

        process = subprocess.Popen([
            'nvidia-docker', 'run', '-d',
            '-e', 'LOCAL_USER_ID=%s' % uid,
            '-v', '%s:/tmp' %args.log_dir,
            '-v', '%s:/app/video' % args.video_dir,
            '--rm',
            'edusense/openpose:'+args.dev,
            '--video', os.path.join('/app', 'video', args.front_video),
            '--num_gpu_start', str(args.front_num_gpu_start),
            '--num_gpu', str(args.front_num_gpu),
            '--use_unix_socket',
            '--unix_socket', os.path.join('/tmp', 'unix.front.sock'),
            '--display', '0',
            '--render_pose', '0',
            '--raw_image'] + real_time_flag,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        front_openpose_container_id = stdout.decode('utf-8').strip()

        print('created front openpose container', front_openpose_container_id)

        process = subprocess.Popen([
            'nvidia-docker', 'run', '-d',
            '-e', 'LOCAL_USER_ID=%s' % uid,
            '-v', '%s:/tmp' %args.log_dir,
            '-v', '%s:/app/video' % args.video_dir,
            '--rm',
            'edusense/openpose:'+args.dev,
            '--video', os.path.join('/app', 'video', args.back_video),
            '--num_gpu_start', str(args.back_num_gpu_start),
            '--num_gpu', str(args.back_num_gpu),
            '--use_unix_socket',
            '--unix_socket', os.path.join('/tmp', 'unix.back.sock'),
            '--display', '0',
            '--render_pose', '0',
            '--raw_image'] + real_time_flag,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        back_openpose_container_id = stdout.decode('utf-8').strip()

        print('created back openpose container', back_openpose_container_id)

        process = subprocess.Popen([
            'docker', 'run', '-d',
            '-e', 'LOCAL_USER_ID=%s' % uid,
            '-e', 'APP_USERNAME=%s' % app_username,
            '-e', 'APP_PASSWORD=%s' % app_password,
            '-v', '%s:/app/video' % args.video_dir,
            '-v', '%s:/tmp' % args.log_dir,
            '--rm',
            'edusense/audio:'+args.dev,
            '--front_url', os.path.join('/app', 'video', args.front_video),
            '--back_url', os.path.join('/app', 'video', args.back_video),
            '--backend_url', args.backend_url,
            '--session_id', session_id,
            '--schema', args.audio_schema],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        audio_container_id = stdout.decode('utf-8').strip()

        print('created audio container', audio_container_id)


        timer = Timer(7200, kill_all_containers, ([
            front_video_container_id,
            front_openpose_container_id,
            back_video_container_id,
            back_openpose_container_id,
            audio_container_id],))
        timer.start()

        process = subprocess.Popen([
            'docker', 'container', 'wait',
            front_video_container_id,
            front_openpose_container_id,
            back_video_container_id,
            back_openpose_container_id,
            audio_container_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        killed_container_ids = stdout.decode('utf-8').split()
        for c in killed_container_ids:
            print('waited container', c)

        timer.cancel()
