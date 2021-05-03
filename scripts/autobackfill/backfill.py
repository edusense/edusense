# Originally from edusense/production: https://github.com/edusense/production

import argparse
import csv
import subprocess
import os
import time
import logging


def rsync_fetch_files(front_url, front_filename, back_url, back_filename):
    # fetch front file
    start_time = time.time()
    process = subprocess.Popen([
        'rsync', '-av', '-e', '\"ssh\"', 'classinsight@%s:%s' % (args.rsync_host, front_url), os.path.join(args.backfill_base_path, front_filename)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logging.debug('rsync done in %f seconds' % (time.time() - start_time))

    start_time = time.time()
    # fetch back file
    process = subprocess.Popen([
        'rsync', '-av', '-e', '\"ssh\"', 'classinsight@%s:%s' % (args.rsync_host, back_url), os.path.join(args.backfill_base_path, back_filename)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    logging.debug('rsync done in %f seconds' % (time.time() - start_time))


def mount_fetch_files(front_url, back_url):
    logging.debug('starting to fetch files from mount')
    # fetch front file
    start_time = time.time()
    subprocess.call('cp %s %s' %
                    (front_url, args.backfill_base_path), shell=True)
    logging.debug('cp done in %f seconds' % (time.time() - start_time))

    # fetch back file
    start_time = time.time()
    subprocess.call('cp %s %s' %
                    (back_url, args.backfill_base_path), shell=True)
    logging.debug('cp done in %f seconds' % (time.time() - start_time))


if __name__ == '__main__':
    logging.basicConfig(filename='autobackfill.log', level=logging.DEBUG)
    logging.debug("Backfill.py")

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
                        required=True, help='connect mode to sync sessions, rsync or mount. check the schedule file for which should be used')
    parser.add_argument('--mount_base_path', dest='mount_base_path', type=str, nargs='?',
                        required=False, help='path of mount')
    parser.add_argument('--backfillFPS', dest='backfillFPS', type=str, nargs='?',
                        required=False, help='FPS for backfill',default=0)
    args = parser.parse_args()

    schedule = []
    with open(args.scheduler_file, 'r') as f:
        reader = csv.reader(f)
        schedule = list(reader)

    logging.debug(" Opened scheduler_file")

    hasMount = False
    if args.sync_mode == 'mount':
        if args.mount_base_path is None:
            logging.debug(" No mount given, default to rsync")
        else:
            hasMount = True

    for s in schedule:
        logging.debug(" looking at ")
        logging.debug(s)

        keyword = s[0]
        time_duration = s[1]
        front_url = s[2]
        front_filename = s[2].split('/')[-1]
        back_url = s[3]
        back_filename = s[3].split('/')[-1]

        logging.debug("{0} {1} {2} {3}".format(
            keyword, time_duration, front_filename, back_filename))

        if hasMount:
            logging.debug(" In mount")
            classes = mount_fetch_files(front_url, back_url)
        else:
            logging.debug(" In rsync")
            classes = rsync_fetch_files(
                front_url, front_filename, back_url, back_filename)

        logging.debug(" Finished getting files, about to call run_backfill.py")

        backfill_script = os.path.join(
            args.backfill_base_path, 'run_backfill.py')
        
        logging.debug("GPU number = " +str(args.gpu_number))
        process = subprocess.Popen([
            '/usr/bin/python3', backfill_script, '--front_video', front_filename, '--back_video', back_filename,
            '--keyword', keyword, '--backend_url', args.backend_url,
            '--front_num_gpu_start', str(args.gpu_number), '--front_num_gpu', '1', '--back_num_gpu_start', str(
                args.gpu_number+1), '--back_num_gpu', '1',
            '--time_duration', str(
                time_duration), '--video_schema', 'classinsight-graphql-video', '--audio_schema', 'classinsight-graphql-audio',
            '--video_dir', args.backfill_base_path, '--developer', args.developer,
            '--backfillFPS',args.backfillFPS],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy())
        stdout, stderr = process.communicate()
        logging.debug(" Output from run_backfill")
        logging.debug(stdout)
        logging.debug(" Error from run_backfill")
        logging.debug(stderr)

        os.remove(os.path.join(args.backfill_base_path, front_filename))
        os.remove(os.path.join(args.backfill_base_path, back_filename))
        logging.debug(" Files removed")
