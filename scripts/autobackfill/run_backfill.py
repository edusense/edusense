#!/usr/bin/python3
import argparse
import json
import os
import sys
import subprocess
import tempfile
import time
import threading
import logging


def get_parameters(run_command):
    uid = os.getuid()
    gid = os.getgid()

    app_username = os.getenv("APP_USERNAME", "")
    app_password = os.getenv("APP_PASSWORD", "")

    logging.debug(run_command)
    logging.debug("APP_USERNAME %s" % (app_username))
    logging.debug("APP_PASSWORD %s" % (app_password))

    # Loading storage server version name
    if run_command == 'run_backfill.py':
        file_location = '../../storage/version.txt'
        f = open(file_location, 'r')
    else:
        try:
            file_location = '../../storage/version.txt'
            f = open(file_location, 'r')
        except:
            file_location = '../../storage/version.txt'
            f = open(file_location, 'r')

    version = f.read()
    version = version.strip('\n')

    # Getting current user
    process = subprocess.Popen(
        ['whoami'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    developer = stdout.decode('utf-8')[:-1]

    return uid, gid, app_username, app_password, version, developer


def kill_all_containers():
    logging.debug('killing all containers')

    process = subprocess.Popen(['docker', 'container', 'kill'] + containers,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    lock.acquire()
    killed_container_ids = stdout.decode('utf-8').split()
    for c in killed_container_ids:
        logging.debug('killed container {0}'.format(c))
    logging.debug(stderr)
    logging.debug("\n")
    lock.release()


def wait_container(container):
    process = subprocess.Popen([
        'docker', 'container', 'wait',
        container],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    process = subprocess.Popen([
        'docker', 'inspect', container, "--format='{{.State.ExitCode}}'"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    status = stdout.decode('utf-8')

    ## logging.debug is not thread-safe
    # acquire a lock
    lock.acquire()
    logging.debug(container_dict[container], "exited with status code", status)
    # remove the container from global list and dict
    # in a thread-safe way
    containers.remove(container)
    del container_dict[container]
    # release lock
    lock.release()


lock = threading.Lock()
# a global list of container id's
containers = []
container_dict = {}

if __name__ == '__main__':
    try:
        os.remove('run_backfill.log')
    except:
        pass
    logging.basicConfig(filename='run_backfill.log', level=logging.DEBUG)
    logging.debug("run_backfill.py")

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
    parser.add_argument('--timeout', dest='timeout', type=int, nargs='?',
                        help='timeout for the script', default=7200)
    parser.add_argument('--log_dir', dest='log_dir', type=str, nargs='?',
                        help='get the logs in a directory')
    parser.add_argument('--video_dir', dest='video_dir', type=str, nargs='?',
                        required=True, help='directory for video')
    parser.add_argument('--process_real_time', dest='process_real_time',
                        action='store_true', help='if set, skip frames to keep'
                        ' realtime')
    parser.add_argument('--tensorflow_gpu', dest='tensorflow_gpu', type=str, nargs='?',
                        default='-1', help='tensorflow gpus')
    parser.add_argument('--overwrite', dest='overwrite', type=str, nargs='?', default='False',
                        help='To enable overwriting previous backfilled session, enter: True')
    args = parser.parse_args()

    uid, gid, app_username, app_password, version, developer = get_parameters(
        sys.argv[0])

    # Calling sessions API endpoint
    process = subprocess.Popen([
        'curl',
        '-X', 'POST',
        '-d', '{\"developer\": \"%s\", \"version\": \"%s\", \"keyword\": \"%s\", \"overwrite\": \"%s\"}' % (
            developer, version, args.keyword, args.overwrite),
        '--header', 'Content-Type: application/json',
        '--basic', '-u', '%s:%s' % (app_username, app_password),
        'https://%s/sessions' % args.backend_url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    logging.debug("stdout from session")
    logging.debug(stdout)
    logging.debug("stderr from session")
    logging.debug(stderr)

    try:
        output = json.loads(stdout.decode('utf-8'))
        success = output['success']
        session_id = output['session_id'].strip()

    except:
        logging.debug("Unable to create a session")
        logging.debug("check APP username and password")
        sys.exit(1)

    logging.debug('created session %s' % (session_id))

    real_time_flag = ['--process_real_time'] if args.process_real_time \
        else []

    # create temp directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        if args.log_dir == None:
            args.log_dir = tmp_dir
            logging.debug('create temporary directory %s' % (tmp_dir))
        process = subprocess.Popen([
            'nvidia-docker', 'run', '-d',
            '-e', 'LOCAL_USER_ID=%s' % uid,
            '-e', 'CUDA_VISIBLE_DEVICES=%s' % args.tensorflow_gpu,
            '-e', 'APP_USERNAME=%s' % app_username,
            '-e', 'APP_PASSWORD=%s' % app_password,
            '-v', '%s:/app/source' % args.video_dir,
            '-v', '%s:/tmp' % args.log_dir,
            'edusense/video:'+args.dev,
            '--video', os.path.join('/app', 'source', args.front_video),
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
        logging.debug("Output of front video container:")
        logging.debug(stdout)
        logging.debug("Error of front video container:")
        logging.debug(stderr)
        front_video_container_id = stdout.decode('utf-8').strip()
        containers.append(front_video_container_id)
        container_dict[front_video_container_id] = 'front video container'
        logging.debug('created front video container %s' %
                      (front_video_container_id))

        process = subprocess.Popen([
            'docker', 'run', '-d',
            '-e', 'LOCAL_USER_ID=%s' % uid,
            '-e', 'APP_USERNAME=%s' % app_username,
            '-e', 'APP_PASSWORD=%s' % app_password,
            '-v', '%s:/tmp' % args.log_dir,
            '-v', '%s:/app/source' % args.video_dir,
            'edusense/video:'+args.dev,
            '--video', os.path.join('/app', 'source', args.back_video),
            '--video_sock', '/tmp/unix.back.sock',
            '--backend_url', args.backend_url,
            '--session_id', session_id,
            '--schema', args.video_schema,
            '--use_unix_socket',
            '--keep_frame_number',
            '--time_duration', str(args.time_duration +
                                   60) if args.time_duration >= 0 else '-1',
            '--process_gaze',
            '--profile',
            '--instructor'] + real_time_flag,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        logging.debug("Output of back video container:")
        logging.debug(stdout)
        logging.debug("Error of back video container:")
        logging.debug(stderr)
        back_video_container_id = stdout.decode('utf-8').strip()
        containers.append(back_video_container_id)
        container_dict[back_video_container_id] = 'back video container'
        logging.debug('created back video container %s' %
                      (back_video_container_id))

        time.sleep(30)

        process = subprocess.Popen([
            'nvidia-docker', 'run', '-d',
            '-e', 'LOCAL_USER_ID=%s' % uid,
            '-v', '%s:/tmp' % args.log_dir,
            '-v', '%s:/app/video' % args.video_dir,
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
        logging.debug("Output of front openpose container:")
        logging.debug(stdout)
        logging.debug("Error of front openpose container:")
        logging.debug(stderr)
        front_openpose_container_id = stdout.decode('utf-8').strip()
        containers.append(front_openpose_container_id)
        container_dict[front_openpose_container_id] = 'front openpose container'
        logging.debug('created front openpose container %s' %
                      (front_openpose_container_id))

        process = subprocess.Popen([
            'nvidia-docker', 'run', '-d',
            '-e', 'LOCAL_USER_ID=%s' % uid,
            '-v', '%s:/tmp' % args.log_dir,
            '-v', '%s:/app/video' % args.video_dir,
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
        logging.debug("Output of back openpose container:")
        logging.debug(stdout)
        logging.debug("Error of back openpose container:")
        logging.debug(stderr)
        back_openpose_container_id = stdout.decode('utf-8').strip()
        containers.append(back_openpose_container_id)
        container_dict[back_openpose_container_id] = 'back openpose container'
        logging.debug('created back openpose container %s' %
                      (back_openpose_container_id))

        process = subprocess.Popen([
            'docker', 'run', '-d',
            '-e', 'LOCAL_USER_ID=%s' % uid,
            '-e', 'APP_USERNAME=%s' % app_username,
            '-e', 'APP_PASSWORD=%s' % app_password,
            '-v', '%s:/app/video' % args.video_dir,
            '-v', '%s:/tmp' % args.log_dir,
            'edusense/audio:'+args.dev,
            '--front_url', os.path.join('/app', 'video', args.front_video),
            '--back_url', os.path.join('/app', 'video', args.back_video),
            '--backend_url', args.backend_url,
            '--session_id', session_id,
            '--time_duration', str(args.time_duration +
                                   60) if args.time_duration >= 0 else '-1',
            '--schema', args.audio_schema],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        logging.debug("Output of audio container:")
        logging.debug(stdout)
        logging.debug("Error of audio container:")
        logging.debug(stderr)
        audio_container_id = stdout.decode('utf-8').strip()
        containers.append(audio_container_id)
        container_dict[audio_container_id] = 'audio container'
        logging.debug('created audio container %s \n\n' % (audio_container_id))

        # the script can be kept running and dockers will be killed after timeout seconds
        timer = threading.Timer(args.timeout, kill_all_containers)
        timer.start()

        # make seperate threads for containers
        threads = []
        for container in containers:
            t = threading.Thread(target=wait_container, args=[container])
            t.start()
            threads.append(t)

        # join the threads
        for thread in threads:
            thread.join()

        # cancel the killing thread execution
        timer.cancel()
