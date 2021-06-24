# Originally from edusense/production: https://github.com/edusense/production

import argparse
import csv
import subprocess
import os
import time
from datetime import datetime
from logging.handlers import WatchedFileHandler
import logging
import base64
import requests


def rsync_fetch_files(front_url, front_filename, back_url, back_filename, logger):
    # fetch front file
    logger.info("Initiating file fetch with rsync for front video")
    start_time = time.time()
    process = subprocess.Popen([
        'rsync', '-av', '-e', '\"ssh\"', 'classinsight@%s:%s' % (args.rsync_host, front_url),
        os.path.join(args.backfill_base_path, front_filename)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logger.info('rsync done in %.3f seconds' % (time.time() - start_time))

    logger.info("Initiating file fetch with rsync for back video")
    start_time = time.time()
    # fetch back file
    process = subprocess.Popen([
        'rsync', '-av', '-e', '\"ssh\"', 'classinsight@%s:%s' % (args.rsync_host, back_url),
        os.path.join(args.backfill_base_path, back_filename)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logger.info('rsync done in %.3f seconds' % (time.time() - start_time))


def mount_fetch_files(front_url, back_url, logger):
    # logger.info('starting to fetch files from mount')
    logger.info("Initiating file fetch with mounted directory for front video")
    # fetch front file
    start_time = time.time()
    subprocess.call('cp %s %s' %
                    (front_url, args.backfill_base_path), shell=True)
    logger.info('cp done in %.3f seconds' % (time.time() - start_time))

    # fetch back file
    logger.info("Initiating file fetch with mounted directory for back video")
    start_time = time.time()
    subprocess.call('cp %s %s' %
                    (back_url, args.backfill_base_path), shell=True)
    logger.info('cp done in %.3f seconds' % (time.time() - start_time))


if __name__ == '__main__':
    # logging.basicConfig(filename='autobackfill.log', level=logging.DEBUG)
    # logging.info("Backfill.py")

    parser = argparse.ArgumentParser(description='EduSense backfill')
    parser.add_argument('--schedule_file', dest='scheduler_file', type=str, nargs='?',
                        required=True, help='schedule file')
    parser.add_argument('--gpu_number', dest='gpu_number', type=int, nargs='?',
                        required=True, help='gpu number')
    parser.add_argument('--backfill_base_path', dest='backfill_base_path', type=str,
                        default='.', help='backfill base path')
    parser.add_argument('--backend_url', dest='backend_url', type=str,
                        required=True, help='backend url')
    parser.add_argument('--rsync_host', dest='rsync_host', type=str,
                        required=True, help='hostname for rsync')
    parser.add_argument('--developer', dest='developer', type=str, nargs='?',
                        required=True, help='username for the docker images')
    parser.add_argument('--sync_mode', dest='sync_mode', type=str, nargs='?',
                        required=True,
                        help='connect mode to sync sessions, rsync or mount. check the schedule file for which should be used')
    parser.add_argument('--mount_base_path', dest='mount_base_path', type=str, nargs='?',
                        required=False, help='path of mount')
    parser.add_argument('--backfillFPS', dest='backfillFPS', type=str, nargs='?',
                        required=False, help='FPS for backfill', default='0')
    parser.add_argument('--log_dir', dest='log_dir', type=str, nargs='?',
                        required=False, help='Log directory to collect backfill logs', default=0)
    args = parser.parse_args()

    logger_master = logging.getLogger('schedule_backfill')
    logger_master.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s | %(process)s, %(thread)d | %(schedule)s | %(name)s | %(levelname)s | %(message)s')
    logging_dict = {
        'schedule': args.scheduler_file.split(".")[0].split("autobackfill")[-1].replace("/","__")
    }

    ## Add core logger handler
    if not os.path.exists(args.log_dir):
        os.makedirs(args.log_dir, 0o777, exist_ok=True)
    time_str = datetime.now().strftime("%Y%m%d")
    core_logging_handler = WatchedFileHandler(f"{args.log_dir}/backfill_{logging_dict['schedule']}.log")
    core_logging_handler.setFormatter(formatter)
    logger_master.addHandler(core_logging_handler)

    ## Add stdout logger handler
    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG)
    console_log.setFormatter(formatter)
    logger_master.addHandler(console_log)

    logger = logging.LoggerAdapter(logger_master, logging_dict)

    logger.info("Reading schedule_file %s for backfill process" % (args.scheduler_file))
    schedule = []
    with open(args.scheduler_file, 'r') as f:
        reader = csv.reader(f)
        schedule = list(reader)

    logger.info("Total %d session backfill requests in schedule_file" % (len(schedule)))

    hasMount = False
    if args.sync_mode == 'mount':
        if args.mount_base_path is None:
            logger.info(" No mount directory given, default fetch files using rsync")
        else:
            hasMount = True

    logger.info("Schedule length:%d" % (len(schedule)))
    for s_idx, s in enumerate(schedule):
        logger.info(f"Processing Session %d:%s from schedule", s_idx, str(s))
        # logger.info(s)

        keyword = s[0]
        time_duration = s[1]
        front_url = s[2]
        front_filename = s[2].split('/')[-1]
        back_url = s[3]
        back_filename = s[3].split('/')[-1]

        logger.info("Session Info: keyword: {0}, Time Limit:{1},  Front Video:{2}, Back Video:{3}".format(
            keyword, time_duration, front_filename, back_filename))

        if hasMount:
            logger.info("Fetching files form mount")
            classes = mount_fetch_files(front_url, back_url, logger)
        else:
            logger.info("Fetching files form rsync")
            classes = rsync_fetch_files(
                front_url, front_filename, back_url, back_filename, logger)

        logger.info("Finished getting files, about to call run_backfill.py")

        backfill_script = os.path.join(
            args.backfill_base_path, 'run_backfill.py')

        logger.info("GPU number = " + str(args.gpu_number))
        run_backfill_command = [
            '/usr/bin/python3', backfill_script, '--front_video', front_filename, '--back_video', back_filename,
            '--keyword', keyword, '--backend_url', args.backend_url,
            '--front_num_gpu_start', str(args.gpu_number), '--front_num_gpu', '1', '--back_num_gpu_start',
            str(args.gpu_number), '--back_num_gpu', '1',
            '--time_duration', str(time_duration), '--video_schema', 'classinsight-graphql-video', '--audio_schema',
            'classinsight-graphql-audio',
            '--video_dir', args.backfill_base_path, '--developer', args.developer,
            '--backfillFPS', args.backfillFPS, '--log_dir', f"{args.log_dir}/{keyword}"]
        logger.info(f"Run backfill command: {'|'.join(run_backfill_command)}")
        process = subprocess.Popen(run_backfill_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   env=os.environ.copy())
        stdout, stderr = process.communicate()
        logger.info("Output from run_backfill")
        logger.info(stdout)
        logger.info("Error from run_backfill")
        logger.info(stderr)

        logger.info("Removing video files from backfill base path")
        os.remove(os.path.join(args.backfill_base_path, front_filename))
        os.remove(os.path.join(args.backfill_base_path, back_filename))
        logger.info(" Files removed")

        # Write backfilling status in db
        # time_str = datetime.now().strftime("%Y%m%d")
        # backfill_logfile = f'{args.log_dir}/{keyword}/run_backfill_{time_str}.log'
        # backfill_logs = None
        # try:
        #     with open(backfill_logfile,'r') as f:
        #         backfill_logs = f.read()
        #     logger.info("Got backfilling logs for writing to db")
        # except:
        #     backfill_logs = ''
        #     logger.info("Unable to get backfilling logs for writing to db")
        #
        # # post to metadata backend
        # backfillmetadata_user = os.getenv("APP_USERNAME", "")
        # backfillmetadata_password = os.getenv("APP_PASSWORD", "")
        # backfillmetadata_url = f"{args.backend_url}/backfillmetadata"
        # cred = '{}:{}'.format(backfillmetadata_user, backfillmetadata_password).encode('ascii')
        # encoded_cred = base64.standard_b64encode(cred).decode('ascii')
        #
        # metadata_payload = {
        #     {
        #         'courseNumber': '15122',
        #         'sessions': [{
        #             'id': 'id4',
        #             'keyword': 'keyword4',
        #             'name': 'name4',
        #             'debugInfo': 'debugInfo4',
        #             'commitId': 'commitId4',
        #             'analyticsCommitId': 'analyticsCommitId4'
        #         }, {
        #             'id': 'id5',
        #             'keyword': 'keyword5',
        #             'name': 'name5',
        #             'debugInfo': 'debugInfo5',
        #             'commitId': 'commitId5',
        #             'analyticsCommitId': 'analyticsCommitId5'
        #         }]
        #     }
        # }
        #
        # # Query template and posting results
        #
        # backend_params = {
        #     'headers': {
        #         'Authorization': 'Basic {}'.format(encoded_cred),
        #         'Content-Type': 'application/json'}
        # }
        #
        # try:
        #     posting_response = requests.post(backfillmetadata_url, headers=backend_params['headers'],
        #                                      json={'analytics': output_payload})
