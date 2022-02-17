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
import traceback
from logging.handlers import WatchedFileHandler
from datetime import datetime, timedelta


def time_diff(t_start, t_end):
    """
    Get time diff in secs
    """
    return (t_end - t_start).seconds + round((t_end - t_start).microseconds / 1000000, 3)

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

    docker_name = stdout.decode('utf-8')[1:-1]
    logger.info("Got docker Name for wait video container process: %s", f"|_{docker_name}_|")
    process = subprocess.Popen([
        'docker', 'wait', docker_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logger.info(f"Docker video {docker_name} wait output: {str(stdout)}, {str(stderr)}")
    process = subprocess.Popen([
        'docker', 'inspect', containers_group['video'], "--format='{{.State.ExitCode}}'"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    status = stdout.decode('utf-8')

    # lock.acquire()
    try:
        logger.info(f"Killing openpose container after video:{containers_group['openpose']}")
        # # Given video container exited, kill openpose container
        process = subprocess.Popen(['docker', 'container', 'kill', containers_group['openpose']],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        logger.info(f"Docker kill openpose after video docker {docker_name} output: {str(stdout)}, {str(stderr)}")
        ## logging.debug is not thread-safe
        # acquire a lock
        # lock.acquire()
        logger.info(
            "%s: %s exited with status code %s" % (keyword, container_dict[containers_group['video']], status))
        # remove the container from global list and dict
        # in a thread-safe way
        # containers.remove(containers_group['video'])
        # del container_dict[containers_group['video']]
        # containers.remove(containers_group['openpose'])
        # del container_dict[containers_group['openpose']]
        logger.info(f"Exiting wait video for {docker_name} gracefully")
    except:
        logger.info("Error in wait video container locked region ", traceback.format_exc())
    # release lock
    # lock.release()


def wait_openpose_container(containers_group, logger):
    # get docker name from id
    process = subprocess.Popen([
        'docker', 'inspect', '--format', '{{.Name}}', containers_group['openpose']],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    docker_name = stdout.decode('utf-8')[1:-1]
    logger.info("Got Docker Name for wait openpose process: %s", f"|_{docker_name}_|")
    process = subprocess.Popen([
        'docker', 'wait', docker_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logger.info(f"Docker openpose {docker_name} wait output: {str(stdout)}, {str(stderr)}")
    process = subprocess.Popen([
        'docker', 'inspect', containers_group['openpose'], "--format='{{.State.ExitCode}}'"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    status = stdout.decode('utf-8')

    # lock.acquire()
    try:
        logger.info(f"Killing video container after openpose:{containers_group['video']}")
        # # Given video container exited, kill openpose container
        process = subprocess.Popen(['docker', 'container', 'kill', containers_group['video']],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        logger.info(f"Docker kill video after openpose docker {docker_name} output: {str(stdout)}, {str(stderr)}")
        ## logging.debug is not thread-safe
        # acquire a lock

        logger.info(
            "%s: %s exited with status code %s" % (keyword, container_dict[containers_group['openpose']], status))
        # remove the container from global list and dict
        # in a thread-safe way
        # containers.remove(containers_group['video'])
        # del container_dict[containers_group['video']]
        # containers.remove(containers_group['openpose'])
        # del container_dict[containers_group['openpose']]
        logger.info(f"Exiting wait openpose for {docker_name} gracefully")
    except:
        logger.info("Error in wait openpose container locked region ", traceback.format_exc())

    # release lock
    # lock.release()

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
    parser.add_argument('--camera_url', dest='camera_url', type=str, nargs='?',
                        default='rtsp://admin:class111_@edusense-livedemo.lan.local.cmu.edu', help='url for ip camera')
    parser.add_argument('--developer', dest='dev', type=str, nargs='?',
                        default='livedemo', help='enter developer tag name')
    parser.add_argument('--backend_url', dest='backend_url', type=str, nargs='?',
                        default='sensei-delta.wv.cc.cmu.edu:3000', help='EduSense backend address')
    parser.add_argument('--log_dir', dest='log_dir', type=str, nargs='?',
                        default='/home/edusense/logs_livedemo', help='get the logs in a directory')
    parser.add_argument('--num_gpu_start', dest='num_gpu_start', type=int, nargs='?',
                        default=0, help='GPU start index for camera processing')
    parser.add_argument('--num_gpu', dest='num_gpu', type=int, nargs='?',
                        default=1, help='number of GPUs for camera processing')
    parser.add_argument('--video_schema', dest='video_schema', type=str, nargs='?',
                        default='classinsight-graphql-video', help='video schema for CI')
    parser.add_argument('--audio_schema', dest='audio_schema', type=str, nargs='?',
                        default='classinsight-graphql-audio', help='audio schema for CI')
    parser.add_argument('--tensorflow_gpu', dest='tensorflow_gpu', type=str, nargs='?',
                        default='-1', help='tensorflow gpus')
    parser.add_argument('--overwrite', dest='overwrite', type=str, nargs='?', default='False',
                        help='To enable overwriting previous backfilled session, enter: True')
    parser.add_argument('--backfillFPS', dest='backfillFPS', type=str, nargs='?',
                        default='0', help='FPS for backfill')
    parser.add_argument('--timeout', dest='timeout', type=int, nargs='?',
                        help='timeout for the script', default=7200)
    # parser.add_argument('--docker_name_prefix', dest='docker_name_prefix', type=str, nargs='?',
    #                     required=False, help='FPS for backfill', default='')
    args = parser.parse_args()

    keyword = datetime.now().strftime("livedemo_%Y%m%d%H%M%S")


    logger_master = logging.getLogger('run_livedemo')
    logger_master.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s | %(process)s, %(thread)d | %(keyword)s | %(name)s | %(levelname)s | %(message)s')
    logging_dict = {
        'keyword': keyword
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


    logger.info(f"Get parameters for backfilling session {keyword}")
    uid, gid, app_username, app_password, version, developer = get_parameters(
        sys.argv[0], logger)


    # Calling sessions API endpoint
    logger.info(f"Create session id for backfilling session: {keyword}")
    t_create_session_id_start = datetime.now()
    process = subprocess.Popen([
        'curl',
        '-X', 'POST',
        '-d', '{\"developer\": \"%s\", \"version\": \"%s\", \"keyword\": \"%s\", \"overwrite\": \"%s\"}' % (
            developer, version, keyword, args.overwrite),
        '--header', 'Content-Type: application/json',
        '--basic', '-u', '%s:%s' % (app_username, app_password),
              'https://%s/sessions' % args.backend_url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    logger.debug("%s: stdout from session" % (keyword))
    logger.debug(stdout)
    logger.debug("%s: stderr from session" % (keyword))
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

    real_time_flag = ['--process_real_time']

    logger.info("Initializing Docker for front video pipeline")
    t_init_front_video_start = datetime.now()

    process = subprocess.Popen([
                                   'docker', 'run', '-d',
                                   '--gpus', 'device=%d' % (args.num_gpu_start),
                                   '-e', 'LOCAL_USER_ID=%s' % uid,
                                   '-e', 'APP_USERNAME=%s' % app_username,
                                   '-e', 'APP_PASSWORD=%s' % app_password,
                                   '--network', 'host',
                                   '-v', '%s:/tmp' % args.log_dir,
                                             'edusense/video:' + args.dev,
                                   '--video', args.camera_url,
                                   '--video_sock', '/tmp/unix.front.sock',
                                   '--backend_url', args.backend_url,
                                   '--session_id', session_id,
                                   '--schema', args.video_schema,
                                   '--use_unix_socket',
                                   '--keep_frame_number',
                                   '--backfillFPS', args.backfillFPS,
                                   '--gaze_3d',
                                   '--time_duration','-1'] + real_time_flag,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logger.debug("%s: Output of front video container:" % (keyword))
    logger.debug(stdout)
    logger.debug("%s: Error of front video container:" % (keyword))
    logger.debug(stderr)
    front_video_container_id = stdout.decode('utf-8').strip()
    containers.append(front_video_container_id)
    front_containers['video'] = front_video_container_id
    container_dict[front_video_container_id] = 'front video container'
    t_init_front_video_end = datetime.now()
    logger.debug('Created front video container for session id %s in %.3f secs', session_id,
                 time_diff(t_init_front_video_start, t_init_front_video_end))

    logger.info("Sleeping for 5 secs...")
    time.sleep(5)
    logger.info("Waking up...")

    logger.info("Initializing nvidia docker for front openpose pipeline")
    t_init_front_openpose_start = datetime.now()

    process = subprocess.Popen([
                                   'nvidia-docker', 'run', '-d',
                                   '-e', 'LOCAL_USER_ID=%s' % uid,
                                   '-v', '%s:/tmp' % args.log_dir,
                                   'edusense/openpose:' + args.dev,
                                   '--ip_camera', args.camera_url,
                                   '--num_gpu_start', str(args.num_gpu_start),
                                   '--num_gpu', str(args.num_gpu),
                                   '--use_unix_socket',
                                   '--unix_socket', os.path.join('/tmp', 'unix.front.sock'),
                                   '--display', '0',
                                   '--render_pose', '0',
                                   '--raw_image'] + real_time_flag,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logger.debug("%s: Output of front openpose container:" % (keyword))
    logger.debug(stdout)
    logger.debug("%s: Error of front openpose container:" % (keyword))
    logger.debug(stderr)
    front_openpose_container_id = stdout.decode('utf-8').strip()
    containers.append(front_openpose_container_id)
    front_containers['openpose'] = front_openpose_container_id
    container_dict[front_openpose_container_id] = 'front openpose container'
    logger.debug('%s: created front openpose container %s' %
                 (keyword, front_openpose_container_id))
    t_init_front_openpose_end = datetime.now()
    logger.debug('Created front openpose container for session id %s in %.3f secs', session_id,
                 time_diff(t_init_front_openpose_start, t_init_front_openpose_end))


    # timer = threading.Timer(args.timeout, kill_all_containers, args=(logger))
    # timer.start()

    # make seperate threads for containers
    threads = []
    t_front_video = threading.Thread(target=wait_video_container, args=(front_containers, logger))
    t_front_video.start()
    t_front_openpose = threading.Thread(target=wait_openpose_container, args=(front_containers, logger))
    t_front_openpose.start()
    t_front_openpose.join()
    logger.debug('front openpose wait container joined for session id %s', session_id)
    t_front_video.join()
    logger.debug('front video wait container joined for session id %s', session_id)

    # cancel the killing thread execution
    # timer.cancel()