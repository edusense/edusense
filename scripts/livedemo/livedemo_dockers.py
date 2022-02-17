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


def kill_containers(containers, logger):
    logger.critical('killing all containers')

    process = subprocess.Popen(['docker', 'container', 'kill'] + containers,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    killed_container_ids = stdout.decode('utf-8').split()
    for c in killed_container_ids:
        logger.critical('killed container {0}'.format(c))
    logger.critical(stderr)
    logger.critical("\n")
    return None


def init_logger(log_dir):
    logger_master = logging.getLogger('run_livedemo')
    logger_master.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s | %(process)s, %(thread)d | %(name)s | %(levelname)s | %(message)s')

    ## Add core logger handler
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    time_str = datetime.now().strftime("%Y%m%d")
    core_logging_handler = WatchedFileHandler(f'{log_dir}/run_livedemo_{time_str}.log')
    core_logging_handler.setFormatter(formatter)
    logger_master.addHandler(core_logging_handler)

    ## Add stdout logger handler
    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG)
    console_log.setFormatter(formatter)
    logger_master.addHandler(console_log)

    logger = logging.LoggerAdapter(logger_master, {})
    return logger


def run_video_docker(camera_url, rmq_exchange, rmq_routing_key, local_user_id, logger, developer='livedemo',
                     log_dir='/home/edusense/logs_livedemo', num_gpu_start=0):
    logger.info("Initializing Docker for video pipeline")
    process = subprocess.Popen([
        'docker', 'run', '-d',
        '--gpus', 'device=%d' % (num_gpu_start),
        '-e', 'LOCAL_USER_ID=%s' % local_user_id,
        '--network', 'host',
        '-v', '%s:/tmp' % log_dir,
                  'edusense/video:' + developer,
        '--video', camera_url,
        '--rabbitmq_exchange', rmq_exchange,
        '--rabbitmq_routing_key', rmq_routing_key,
        '--video_sock', '/tmp/unix.front.sock',
        '--use_unix_socket',
        '--keep_frame_number',
        '--gaze_3d',
        '--time_duration', '-1', '--process_real_time'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logger.debug("%s: Output of video container:" % (stdout))
    logger.debug("%s: Error of video container:" % (stderr))
    video_container_id = stdout.decode('utf-8').strip()
    return video_container_id


def run_openpose_docker(camera_url, local_user_id,logger, developer='livedemo', log_dir='/home/edusense/logs_livedemo',
                        num_gpu_start=0,
                        num_gpu=1):
    logger.info("Initializing nvidia docker for openpose pipeline")
    process = subprocess.Popen([
        'nvidia-docker', 'run', '-d',
        '-e', 'LOCAL_USER_ID=%s' % local_user_id,
        '-v', '%s:/tmp' % log_dir,
              'edusense/openpose:' + developer,
        '--ip_camera', camera_url,
        '--num_gpu_start', str(num_gpu_start),
        '--num_gpu', str(num_gpu),
        '--use_unix_socket',
        '--unix_socket', os.path.join('/tmp', 'unix.front.sock'),
        '--display', '0',
        '--render_pose', '0',
        '--raw_image', '--process_real_time'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logger.debug("%s: Output of openpose container:" % (stdout))
    logger.debug("%s: Error of openpose container:" % (stderr))
    openpose_container_id = stdout.decode('utf-8').strip()
    return openpose_container_id
