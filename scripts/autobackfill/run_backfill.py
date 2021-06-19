#!/usr/bin/python3
import argparse
import json
import os
import sys
import subprocess
import tempfile
# import uuid
import time
import threading
import logging
from logging.handlers import WatchedFileHandler
from datetime import datetime, timedelta
from time_utils import time_diff


def get_parameters(run_command, logger):
    uid = os.getuid()
    gid = os.getgid()

    app_username = os.getenv("APP_USERNAME", "")
    app_password = os.getenv("APP_PASSWORD", "")

    # logger.debug("%s: APP_USERNAME %s" % (args.keyword, app_username))
    # logger.debug("%s: APP_PASSWORD %s" % (args.keyword, app_password))

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

    logger.info(f"Got UserId:{str(uid)}, GroupId:{str(gid)},Version:{str(version)},Developer:{str(developer)}")

    return uid, gid, app_username, app_password, version, developer


def kill_all_containers(logger):
    logger.critical('killing all containers')

    process = subprocess.Popen(['docker', 'container', 'kill'] + containers,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    lock.acquire()
    killed_container_ids = stdout.decode('utf-8').split()
    for c in killed_container_ids:
        logger.critical('killed container {0}'.format(c))
    logger.critical(stderr)
    logger.critical("\n")
    lock.release()


def wait_video_container(containers_group, logger):
    # get docker name from id
    process = subprocess.Popen([
        'docker', 'inspect', '--format', '{{.Name}}', containers_group['video']],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    docker_name = stdout.decode('utf-8')
    logger.info("Got Docker Name for Wait process: %s", f"|_{docker_name}_|")
    process = subprocess.Popen([
        'docker', 'wait', docker_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logger.info(f"Docker wait output: {str(stdout)}, {str(stderr)}")
    process = subprocess.Popen([
        'docker', 'inspect', containers_group['video'], "--format='{{.State.ExitCode}}'"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    status = stdout.decode('utf-8')

    lock.acquire()
    logger.info(f"Killing openpose container:{containers_group['openpose']}")
    # # Given video container exited, kill openpose container
    process = subprocess.Popen(['docker', 'container', 'kill', containers_group['openpose']],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    ## logging.debug is not thread-safe
    # acquire a lock

    logger.info("%s: %s exited with status code %s" % (args.keyword, container_dict[containers_group['video']], status))
    # remove the container from global list and dict
    # in a thread-safe way
    containers.remove(containers_group['video'])
    del container_dict[containers_group['video']]
    containers.remove(containers_group['openpose'])
    del container_dict[containers_group['openpose']]

    # release lock
    lock.release()


def wait_audio_container(containers_group, logger):
    process = subprocess.Popen([
        'docker', 'wait', 'CONTAINER',
        containers_group['audio']],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    process = subprocess.Popen([
        'docker', 'inspect', containers_group['audio'], "--format='{{.State.ExitCode}}'"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    status = stdout.decode('utf-8')

    ## logging.debug is not thread-safe
    # acquire a lock
    lock.acquire()
    logger.debug(
        "%s: %s exited with status code %s" % (args.keyword, container_dict[containers_group['audio']], status))
    # remove the container from global list and dict
    # in a thread-safe way
    containers.remove(containers_group['audio'])
    del container_dict[containers_group['audio']]
    # release lock
    lock.release()


lock = threading.Lock()
# a global list of container id's
containers = []
front_containers = {}
back_containers = {}
audio_containers = {}
container_dict = {}

if __name__ == '__main__':
    # logging.basicConfig(filename='run_backfill.log', level=logging.DEBUG)
    # logging.debug("run_backfill.py")

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
                        required=True, help='get the logs in a directory')
    parser.add_argument('--video_dir', dest='video_dir', type=str, nargs='?',
                        required=True, help='directory for video')
    parser.add_argument('--process_real_time', dest='process_real_time',
                        action='store_true', help='if set, skip frames to keep'
                                                  ' realtime')
    parser.add_argument('--tensorflow_gpu', dest='tensorflow_gpu', type=str, nargs='?',
                        default='-1', help='tensorflow gpus')
    parser.add_argument('--overwrite', dest='overwrite', type=str, nargs='?', default='False',
                        help='To enable overwriting previous backfilled session, enter: True')
    parser.add_argument('--backfillFPS', dest='backfillFPS', type=str, nargs='?',
                        required=False, help='FPS for backfill', default='0')
    # parser.add_argument('--docker_name_prefix', dest='docker_name_prefix', type=str, nargs='?',
    #                     required=False, help='FPS for backfill', default='')
    args = parser.parse_args()

    logger_master = logging.getLogger('run_backfill')
    logger_master.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s | %(process)s, %(thread)d | %(keyword)s | %(name)s | %(levelname)s | %(message)s')
    logging_dict = {
        'keyword': args.keyword
    }

    ## Add core logger handler
    if not os.path.exists(args.log_dir):
        os.makedirs(args.log_dir)
    time_str = datetime.now().strftime("%Y%m%d")
    core_logging_handler = WatchedFileHandler(f'{args.log_dir}/run_backfill_{time_str}.log')
    core_logging_handler.setFormatter(formatter)
    logger_master.addHandler(core_logging_handler)

    ## Add stdout logger handler
    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG)
    console_log.setFormatter(formatter)
    logger_master.addHandler(console_log)

    logger = logging.LoggerAdapter(logger_master, logging_dict)

    logger.info(f"Get parameters for backfilling session {args.keyword}")
    uid, gid, app_username, app_password, version, developer = get_parameters(
        sys.argv[0], logger)

    # curl_comm = [
    #     'curl',
    #     '-X', 'POST',
    #     '-d', '{\"developer\": \"%s\", \"version\": \"%s\", \"keyword\": \"%s\", \"overwrite\": \"%s\"}' % (
    #         developer, version, args.keyword, args.overwrite),
    #     '--header', 'Content-Type: application/json',
    #     '--basic', '-u', '%s:%s' % (app_username, app_password),
    #     'https://%s/sessions' % args.backend_url]

    # logging.debug(curl_comm)

    # Calling sessions API endpoint
    logger.info(f"Create session id for backfilling session: {args.keyword}")
    t_create_session_id_start = datetime.now()
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

    logger.debug("%s: stdout from session" % (args.keyword))
    logger.debug(stdout)
    logger.debug("%s: stderr from session" % (args.keyword))
    logger.debug(stderr)

    try:
        output = json.loads(stdout.decode('utf-8'))
        success = output['success']
        session_id = output['session_id'].strip()
        t_create_session_id_end = datetime.now()
        logger.info(f"Created session id %s in %.3f secs", session_id,
                    time_diff(t_create_session_id_start, t_create_session_id_end))

    except:
        logger.debug("Unable to create a session")
        logger.debug("check APP username and password")
        sys.exit(1)

    # logger.debug('%s: created session %s' % (args.keyword, session_id))

    real_time_flag = ['--process_real_time'] if args.process_real_time \
        else []

    vid_comm = [
                   'docker', 'run', '-d',
                   '--gpus', 'device=%d' % (args.front_num_gpu_start),
                   '-e', 'LOCAL_USER_ID=%s' % uid,
                   '-e', 'APP_USERNAME=%s' % app_username,
                   '-e', 'APP_PASSWORD=%s' % app_password,
                   '-v', '%s:/app/source' % args.video_dir,
                   '-v', '%s:/tmp' % args.log_dir,
                             'edusense/video:' + args.dev,
                   '--video', os.path.join('/app', 'source', args.front_video),
                   '--backend_url', args.backend_url,
                   '--session_id', session_id,
                   '--backfillFPS', args.backfillFPS,
                   '--time_duration',
                   str(args.time_duration + 60) if args.time_duration >= 0 else '-1'] + real_time_flag
    logger.debug(" | ".join(vid_comm))

    # create temp directory(made log_dir mandate for run backfill
    # with tempfile.TemporaryDirectory() as tmp_dir:
    #     if args.log_dir == None:
    #         args.log_dir = tmp_dir
    #         logging.debug('%s: create temporary directory %s' % (args.keyword, tmp_dir))

    # Set docker name prefix if nor already set
    # if args.docker_name_prefix == '':
    #     docker_name_prefix = str(uuid.uuid4())
    #     logger.info("Generating random docker name prefix: %s", docker_name_prefix)
    logger.info("Initializing Docker for front video pipeline")
    t_init_front_video_start = datetime.now()

    process = subprocess.Popen([
                                   'docker', 'run', '-d',
                                   '--gpus', 'device=%d' % (args.front_num_gpu_start),
                                   '-e', 'LOCAL_USER_ID=%s' % uid,
                                   '-e', 'APP_USERNAME=%s' % app_username,
                                   '-e', 'APP_PASSWORD=%s' % app_password,
                                   '-v', '%s:/app/source' % args.video_dir,
                                   '-v', '%s:/tmp' % args.log_dir,
                                             'edusense/video:' + args.dev,
                                   '--video', os.path.join('/app', 'source', args.front_video),
                                   '--video_sock', '/tmp/unix.front.sock',
                                   '--backend_url', args.backend_url,
                                   '--session_id', session_id,
                                   '--schema', args.video_schema,
                                   '--use_unix_socket',
                                   '--keep_frame_number',
                                   '--backfillFPS', args.backfillFPS,
                                   '--gaze_3d',
                                   '--time_duration',
                                   str(args.time_duration + 60) if args.time_duration >= 0 else '-1'] + real_time_flag,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logger.debug("%s: Output of front video container:" % (args.keyword))
    logger.debug(stdout)
    logger.debug("%s: Error of front video container:" % (args.keyword))
    logger.debug(stderr)
    front_video_container_id = stdout.decode('utf-8').strip()
    containers.append(front_video_container_id)
    front_containers['video'] = front_video_container_id
    container_dict[front_video_container_id] = 'front video container'
    t_init_front_video_end = datetime.now()
    logger.debug('Created front video container for session id %s in %.3f secs', session_id,
                 time_diff(t_init_front_video_start, t_init_front_video_end))

    logger.info("Initializing Docker for back video pipeline")
    t_init_back_video_start = datetime.now()

    process = subprocess.Popen([
                                   'docker', 'run', '-d',
                                   '--gpus', 'device=%d' % (args.back_num_gpu_start),
                                   '-e', 'LOCAL_USER_ID=%s' % uid,
                                   '-e', 'APP_USERNAME=%s' % app_username,
                                   '-e', 'APP_PASSWORD=%s' % app_password,
                                   '-v', '%s:/tmp' % args.log_dir,
                                   '-v', '%s:/app/source' % args.video_dir,
                                             'edusense/video:' + args.dev,
                                   '--video', os.path.join('/app', 'source', args.back_video),
                                   '--video_sock', '/tmp/unix.back.sock',
                                   '--backend_url', args.backend_url,
                                   '--session_id', session_id,
                                   '--schema', args.video_schema,
                                   '--gaze_3d',
                                   '--use_unix_socket',
                                   '--backfillFPS', args.backfillFPS,
                                   '--keep_frame_number',
                                   '--time_duration', str(args.time_duration +
                                                          60) if args.time_duration >= 0 else '-1',
                                   '--instructor'] + real_time_flag,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logger.debug("%s: Output of back video container:" % (args.keyword))
    logger.debug(stdout)
    logger.debug("%s: Error of back video container:" % (args.keyword))
    logger.debug(stderr)
    back_video_container_id = stdout.decode('utf-8').strip()
    containers.append(back_video_container_id)
    back_containers['video'] = back_video_container_id
    container_dict[back_video_container_id] = 'back video container'
    # logger.debug('%s: created back video container %s' %
    #               (args.keyword, back_video_container_id))

    t_init_back_video_end = datetime.now()
    logger.debug('Created back video container for session id %s in %.3f secs', session_id,
                 time_diff(t_init_back_video_start, t_init_back_video_end))

    logger.info("Sleeping for 30 secs...")
    time.sleep(30)
    logger.info("Waking up...")

    logger.info("Initializing nvidia docker for front openpose pipeline")
    t_init_front_openpose_start = datetime.now()

    process = subprocess.Popen([
                                   'nvidia-docker', 'run', '-d',
                                   '-e', 'LOCAL_USER_ID=%s' % uid,
                                   '-v', '%s:/tmp' % args.log_dir,
                                   '-v', '%s:/app/video' % args.video_dir,
                                         'edusense/openpose:' + args.dev,
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
    logger.debug("%s: Output of front openpose container:" % (args.keyword))
    logger.debug(stdout)
    logger.debug("%s: Error of front openpose container:" % (args.keyword))
    logger.debug(stderr)
    front_openpose_container_id = stdout.decode('utf-8').strip()
    containers.append(front_openpose_container_id)
    front_containers['openpose'] = front_openpose_container_id
    container_dict[front_openpose_container_id] = 'front openpose container'
    logger.debug('%s: created front openpose container %s' %
                 (args.keyword, front_openpose_container_id))
    t_init_front_openpose_end = datetime.now()
    logger.debug('Created front openpose container for session id %s in %.3f secs', session_id,
                 time_diff(t_init_front_openpose_start, t_init_front_openpose_end))

    logger.info("Initializing nvidia docker for back openpose pipeline")
    t_init_back_openpose_start = datetime.now()

    process = subprocess.Popen([
                                   'nvidia-docker', 'run', '-d',
                                   '-e', 'LOCAL_USER_ID=%s' % uid,
                                   '-v', '%s:/tmp' % args.log_dir,
                                   '-v', '%s:/app/video' % args.video_dir,
                                         'edusense/openpose:' + args.dev,
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
    logger.debug("%s: Output of back openpose container:" % (args.keyword))
    logger.debug(stdout)
    logger.debug("%s: Error of back openpose container:" % (args.keyword))
    logger.debug(stderr)
    back_openpose_container_id = stdout.decode('utf-8').strip()
    containers.append(back_openpose_container_id)
    back_containers['openpose'] = back_openpose_container_id
    container_dict[back_openpose_container_id] = 'back openpose container'
    logger.debug('%s: created back openpose container %s' %
                 (args.keyword, back_openpose_container_id))

    t_init_back_openpose_end = datetime.now()
    logger.debug('Created back openpose container for session id %s in %.3f secs', session_id,
                 time_diff(t_init_back_openpose_start, t_init_back_openpose_end))

    logger.info("Initializing docker for audio pipeline")
    t_init_audio_start = datetime.now()

    process = subprocess.Popen([
        'docker', 'run', '-d',
        '-e', 'LOCAL_USER_ID=%s' % uid,
        '-e', 'APP_USERNAME=%s' % app_username,
        '-e', 'APP_PASSWORD=%s' % app_password,
        '-v', '%s:/app/video' % args.video_dir,
        '-v', '%s:/tmp' % args.log_dir,
              'edusense/audio:' + args.dev,
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
    logger.debug("%s: Output of audio container:" % (args.keyword))
    logger.debug(stdout)
    logger.debug("%s: Error of audio container:" % (args.keyword))
    logger.debug(stderr)
    audio_container_id = stdout.decode('utf-8').strip()
    audio_containers['audio'] = audio_container_id
    containers.append(audio_container_id)
    container_dict[audio_container_id] = 'audio container'
    logger.debug('%s: created audio container %s \n\n' % (args.keyword, audio_container_id))

    t_init_audio_end = datetime.now()
    logger.debug('Created audio container for session id %s in %.3f secs', session_id,
                 time_diff(t_init_audio_start, t_init_audio_end))

    # the script can be kept running and dockers will be killed after timeout seconds

    timer = threading.Timer(args.timeout, kill_all_containers, args=(logger))
    timer.start()

    # make seperate threads for containers
    threads = []
    t_front = threading.Thread(target=wait_video_container, args=(front_containers, logger))
    t_front.start()
    t_back = threading.Thread(target=wait_video_container, args=(back_containers, logger))
    t_back.start()
    t_audio = threading.Thread(target=wait_audio_container, args=(audio_containers, logger))
    t_audio.start()

    t_audio.join()
    t_back.join()
    t_front.join()

    # for container in containers:
    #     t = threading.Thread(target=wait_container, args=[container])
    #     t.start()
    #     threads.append(t)

    # join the threads
    # for thread in threads:
    #     thread.join()

    # cancel the killing thread execution
    timer.cancel()
