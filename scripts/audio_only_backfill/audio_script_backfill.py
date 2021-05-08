import argparse
import datetime
import os
import subprocess
import sys
import tempfile
import csv
import json
import logging
import time
from logging.handlers import WatchedFileHandler

# Initialize logging handlers

logger_master = logging.getLogger('autobackfill_audio')
logger_master.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s | %(process)s, %(thread)d | %(name)s | %(levelname)s | %(message)s')

## Add core logger handler

core_logging_handler = WatchedFileHandler('logs/autobackfill_audio.log')
core_logging_handler.setFormatter(formatter)
logger_master.addHandler(core_logging_handler)

## Add stdout logger handler
console_log = logging.StreamHandler()
console_log.setLevel(logging.DEBUG)
console_log.setFormatter(formatter)
logger_master.addHandler(console_log)

logger = logging.LoggerAdapter(logger_master, {})


def get_parameters():
    uid = os.getuid()
    gid = os.getgid()

    app_username = os.getenv("APP_USERNAME", "")
    app_password = os.getenv("APP_PASSWORD", "")

    # logging.debug("%s: APP_USERNAME %s" % (args.keyword, app_username))
    # logging.debug("%s: APP_PASSWORD %s" % (args.keyword, app_password))

    # Loading storage server version name

    file_location = '../../storage/version.txt'
    f = open(file_location, 'r')

    version = f.read()
    version = version.strip('\n')
    f.close()

    # Getting current user
    process = subprocess.Popen(
        ['whoami'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    developer = stdout.decode('utf-8')[:-1]

    return uid, gid, app_username, app_password, version, developer


def mount_fetch_files(front_url, back_url, basepath):
    logger.debug('starting to fetch files from mount')
    # fetch front file
    start_time = time.time()
    subprocess.call('cp %s %s' %
                    (front_url, basepath), shell=True)
    logger.debug('cp done in %f seconds' % (time.time() - start_time))

    # fetch back file
    start_time = time.time()
    subprocess.call('cp %s %s' %
                    (back_url, basepath), shell=True)
    logger.debug('cp done in %f seconds' % (time.time() - start_time))


if __name__ == '__main__':
    logger.info("Starting auto audiobackfill...")
    logger.info("Parsing command line arguments")
    # process arguments
    parser = argparse.ArgumentParser(description='prepare audio only backfill')
    parser.add_argument('--backend_url', dest='backend_url', type=str, nargs='?',
                        required=True, help='edusense backend url')
    parser.add_argument('--mount_base_path', dest='mount_base_path', type=str, nargs='?',
                        required=True, help='path of mount')
    parser.add_argument('--keyword_file', dest='keyword_file', type=str, nargs='?',
                        required=False, help='keyword for class sessions',
                        default='session_keyword_file.csv')
    parser.add_argument('--basepath', dest='basepath', type=str, nargs='?',
                        required=False, help='keyword for class sessions')
    parser.add_argument('--log_dir', dest='log_dir', type=str, nargs='?',
                        help='get the logs in a directory')
    args = parser.parse_args()

    # Loop over csv to run audio pipeline
    logger.info("Looping over session keyword file")
    with open("session_keyword_file.csv") as f:
        for line in f.readlines():
            session_keyword = line[:-1]
            logger.info(f"Running backfill for session keyword {session_keyword}")
            folders = ['2019S', '2019M', '2019F']

            for folder in folders:
                front_url = f"{args.mount_base_path}/{folder}/video_backup/" \
                            f"classinsight-{session_keyword}/classinsight-{session_keyword}" \
                            f"-front.avi"
                back_url = f"{args.mount_base_path}/{folder}/video_backup/" \
                           f"classinsight-{session_keyword}/classinsight-{session_keyword}" \
                           f"-back.avi"

                if os.path.exists(front_url) & os.path.exists(back_url):
                    logger.info(f"Fetching files from {folder} on mounted NAS")
                    if (not os.path.exists(f"{args.basepath}/{front_url.split('/')[-1]}")) | (
                            not os.path.exists(f"{args.basepath}/{back_url.split('/')[-1]}")):
                        mount_fetch_files(front_url, back_url, args.basepath)
                    logger.info(f"Fetch files successful.")
                    break
                else:
                    continue

            front_file = f"classinsight-{session_keyword}-front.avi"
            back_file = f"classinsight-{session_keyword}-back.avi"

            # create a session id
            logger.info(f"Getting session parameters for keyword: {session_keyword}")
            uid, gid, app_username, app_password, version, developer = get_parameters()
            # Calling sessions API endpoint
            logger.info(f"Creating session id for keyword: {session_keyword}")
            process = subprocess.Popen([
                'curl',
                '-X', 'POST',
                '-d', '{\"developer\": \"%s\", \"version\": \"%s\", \"keyword\": \"%s\", \"overwrite\": \"%s\"}' % (
                    developer, version, session_keyword, False),
                '--header', 'Content-Type: application/json',
                '--basic', '-u', '%s:%s' % (app_username, app_password),
                      'https://%s/sessions' % args.backend_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            try:
                output = json.loads(stdout.decode('utf-8'))
                success = output['success']
                session_id = output['session_id'].strip()

            except:
                logger.debug("Unable to create a session")
                logger.debug("check APP username and password")
                sys.exit(1)

            # Run pipeline directly

            logger.info(f"Running pipeline for session id: {session_id}")

            pipeline_run_command = f"python3 audio_pipeline.py --front_url {args.basepath + '/' + front_file} --back_url {args.basepath + '/' + back_file} --backend_url {args.backend_url} --session_id {session_id} --schema classinsight-graphql-audio"

            logger.info(f"Running pipeline command: {pipeline_run_command}")

            os.system(pipeline_run_command)

            logger.info(f"Pipeline execution finished")

            os.remove(os.path.join(args.basepath, front_file))
            os.remove(os.path.join(args.basepath, back_file))
            logger.info(f"Removed video files for session id: {session_id}")
