# Originally from edusense/production: https://github.com/edusense/production

import argparse
from datetime import datetime
from logging.handlers import WatchedFileHandler
import os
import subprocess
import sys

import tempfile
import csv
import logging

# duration for each class
metadata = {
    # '05418A': 10
}

NUM_GPUS = 7


def writelog(message, f):
    if f is not None:
        f.write(message + '\n')


def rsync_get_classes(logger):
    logger.info("* in rsync_get_files")
    rsync_path = 'classinsight@%s:%s/video_backup' % (
        args.rsync_host, args.rsync_base_path)
    process = subprocess.Popen([
        'rsync', '-av', '-e', '\"ssh\"', '--list-only', rsync_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    lines = filter(lambda x: 'avi' in x and args.keyword in x,
                   stdout.decode('utf-8').split('\n'))

    classes = {}
    for line in lines:
        filepath = line.split()[4]
        keyword = filepath.split('/')[1].replace('classinsight-', '')

        fullpath = args.rsync_base_path + "/" + filepath

        if keyword in classes.keys():
            if 'front' in filepath:
                classes[keyword]['front'] = fullpath
            else:
                classes[keyword]['back'] = fullpath
        else:
            if 'front' in filepath:
                classes[keyword] = {
                    'front': fullpath
                }
            else:
                classes[keyword] = {
                    'back': fullpath
                }
    return classes


def mount_get_classes(logger):
    logger.info("Fetching classes info from mount based on keyword")
    mount_path = '%s/video_backup' % (args.mount_base_path)
    allfiles = os.walk(mount_path)
    classes = {}

    for subdir, dirs, files in allfiles:
        for filename in files:
            filepath = subdir + os.sep + filename

            if 'avi' in filepath and args.keyword in filepath:
                keyword = subdir.split('/')[-1].replace('classinsight-', '')

                if keyword in classes.keys():
                    if 'front' in filename:
                        classes[keyword]['front'] = filepath
                        logger.info("adding file %s into keyword %s", filename, keyword)
                    else:
                        classes[keyword]['back'] = filepath
                        logger.info("adding file %s into keyword %s", filename, keyword)
                else:
                    if 'front' in filename:
                        classes[keyword] = {
                            'front': filepath
                        }
                        logger.info("adding file %s into created keyword %s", filename, keyword)
                    else:
                        classes[keyword] = {
                            'back': filepath
                        }
                        logger.info("adding file %s into created keyword %s", filename, keyword)
    logger.info("Finished fetching classes information from mount.")
    return classes


if __name__ == '__main__':
    # try:
    #     os.remove('autobackfill.log')
    # except:
    #     pass
    #
    # try:
    #     os.remove('run_backfill.log')
    # except:
    #     pass

    # logging.basicConfig(filename='autobackfill.log', level=logging.DEBUG)
    # logging.info("Autobackfill.py")

    parser = argparse.ArgumentParser(description='prepare backfill')
    parser.add_argument('--rsync_host', dest='rsync_host', type=str, nargs='?',
                        required=True, help='rsync host name')
    parser.add_argument('--rsync_base_path', dest='rsync_base_path', type=str, nargs='?',
                        required=True, help='rsync base path')
    parser.add_argument('--backfill_base_path', dest='backfill_base_path', type=str, nargs='?',
                        required=True, help='base path for backfill')
    parser.add_argument('--backend_url', dest='backend_url', type=str, nargs='?',
                        required=True, help='edusense backend url')
    parser.add_argument('--keyword', dest='keyword', type=str, nargs='?',
                        required=True, help='keyword for class sessions')
    parser.add_argument('--developer', dest='developer', type=str, nargs='?',
                        required=True, help='username for the docker images')
    parser.add_argument('--sync_mode', dest='sync_mode', type=str, nargs='?',
                        required=True, help='connect mode to sync sessions, rsync or mount')
    parser.add_argument('--mount_base_path', dest='mount_base_path', type=str, nargs='?',
                        required=False, help='path of mount')
    parser.add_argument('--backfillFPS', dest='backfillFPS', type=str, nargs='?',
                        required=False, help='FPS for backfill', default='0')
    parser.add_argument('--log_dir', dest='log_dir', type=str, nargs='?',
                        required=False, help='Log directory to collect autobackfill logs', default=0)
    args = parser.parse_args()

    logger_master = logging.getLogger('auto_backfill')
    logger_master.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s | %(process)s, %(thread)d | %(keyword)s | %(name)s | %(levelname)s | %(message)s')
    logging_dict = {
        'keyword': args.keyword
    }

    ## Add core logger handler
    if not os.path.exists(args.log_dir):
        os.makedirs(args.log_dir, 0o777, exist_ok=True)
    time_str = datetime.now().strftime("%Y%m%d")
    core_logging_handler = WatchedFileHandler(f"{args.log_dir}/autobackfill_{logging_dict['keyword']}.log")
    core_logging_handler.setFormatter(formatter)
    logger_master.addHandler(core_logging_handler)

    ## Add stdout logger handler
    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG)
    console_log.setFormatter(formatter)
    logger_master.addHandler(console_log)

    logger = logging.LoggerAdapter(logger_master, logging_dict)

    time_str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    logger.info("--------------------------Starting new autobackfill session at %s--------------------------", time_str)

    if args.sync_mode != 'rsync' and args.sync_mode != 'mount':
        raise Exception('sync_mode must be either \'rsync\' or \'mount\'')

    if args.sync_mode == 'mount':
        logger.info("Collecting information from mount")
        if args.mount_base_path is None:
            logger.info(" No mount given, default to rsync")
            classes = rsync_get_classes(logger)
        else:
            classes = mount_get_classes(logger)
    elif args.sync_mode == 'rsync':
        logger.info(" Rsync")
        classes = rsync_get_classes(logger)

    logger.info(" Parsed %d classes", len(classes))
    # logger.info(classes)

    schedules = []
    num_schedules = NUM_GPUS - 1  # leaving 1 GPU for openpose binary processing

    logger.info(f"Creating {str(num_schedules)} schedules for {str(NUM_GPUS)} GPUs")

    if num_schedules < 1:
        logger.error("Number of GPUs less than 1. exiting..")
        exit(0)

    for k, v in classes.items():
        if 'front' in v.keys() and 'back' in v.keys():
            COURSE = k.split('_')[1]
            if COURSE in metadata.keys():
                time = metadata[COURSE]
            else:
                time = -1
            schedule_entry = [k, time, v['front'].strip(), v['back'].strip()]
            schedules.append(schedule_entry)
            logger.info(f"Parsed schedule: {str(schedule_entry)}")

    logger.info("Parsed total %d schedule entries", len(schedules))
    # logger.info(schedules)
    ## make the directory
    process_time = datetime.now().strftime('%Y%m%d%H%M')
    directory = os.path.join(args.backfill_base_path,
                             '%s:%s' % (args.keyword, process_time))
    access_rights = 0o770
    os.makedirs(directory, access_rights, exist_ok=True)

    logger.info("Created directory %s for this autobackfill session", directory)
    ##[[], [], [], []]
    ## round-robin to divide the task
    logger.info("Round robin to divide task across multiple threads")
    subschedules = [list() for i in range(num_schedules)]
    for i in range(len(schedules)):
        subschedules[i % num_schedules].append(schedules[i])

    logger.info("Writing subschedules in files")
    for i in range(len(subschedules)):
        with open(os.path.join(directory, 'schedule-%d.csv' % i), 'w') as f:
            writer = csv.writer(f)
            for s in subschedules[i]:
                writer.writerow(s)

    logger.info("Calling one backfill.py for each subschedule independently")

    processes = []

    for i in range(len(subschedules)):
        logger.info("Calling backfill for subschedule %d", i)
        process = subprocess.Popen([
            '/usr/bin/python3', os.path.join(
                args.backfill_base_path, 'backfill.py'),
            '--schedule_file', os.path.join(directory, 'schedule-%d.csv' % i),
            '--gpu_number', '%d' % (i+1),
            '--backfill_base_path', args.backfill_base_path,
            '--backend_url', args.backend_url,
            '--rsync_host', args.rsync_host,
            '--developer', args.developer,
            '--sync_mode', args.sync_mode,
            '--backfillFPS', args.backfillFPS,
            '--mount_base_path', args.mount_base_path,
            '--log_dir', args.log_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy())
        processes.append(process)

    logger.info("Waiting on joining threads from all subschedules")
    for i in range(len(subschedules)):
        stdout, stderr = processes[i].communicate()
        logger.info("subschedule %d finished processing", i)
        logger.info("subschedule %d std output: %s", i, stdout.decode('utf-8'))
        with open(os.path.join(directory, 'schedule-%d.stdout' % i), 'a') as f:
            f.write(stdout.decode('utf-8'))
        logger.info("subschedule %d std error: %s", i, stderr.decode('utf-8'))
        with open(os.path.join(directory, 'schedule-%s.stderr' % i), 'a') as f:
            f.write(stderr.decode('utf-8'))
