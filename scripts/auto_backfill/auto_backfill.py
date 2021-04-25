# Originally from edusense/production: https://github.com/edusense/production

import argparse
import datetime
import os
import subprocess
import sys
import tempfile
import csv

# duration for each class
metadata = {
    'course_number': 3000
}

if __name__ == '__main__':
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
    args = parser.parse_args()

    rsync_path = 'classinsight@%s:%s/video_backup' % (args.rsync_host, args.rsync_base_path)
    process = subprocess.Popen([
        'rsync', '-av', '-e', '\"ssh\"', '--list-only', rsync_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    lines = filter(lambda x: 'avi' in x and args.keyword in x, stdout.decode('utf-8').split('\n'))

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

    schedules = []
    for k, v in classes.items():
        if 'front' in v.keys() and 'back' in v.keys():
            schedules.append([k, metadata[k.split('_')[1]], v['front'].strip(), v['back'].strip()])

    process_time = datetime.datetime.now().strftime('%Y%m%d%H%M')
    directory = os.path.join(args.backfill_base_path, '%s:%s' % (args.keyword, process_time))

    access_rights = 0o770
    os.makedirs(directory, access_rights, exist_ok=True)

    subschedules = [list() for i in range(4)]
    for i in range(len(schedules)):
        subschedules[i%4].append(schedules[i])

    for i in range(len(subschedules)):
        with open(os.path.join(directory, 'schedule-%d.csv' % i), 'w') as f:
            writer = csv.writer(f)
            for s in subschedules[i]:
                writer.writerow(s)

    processes = []
    for i in range(len(subschedules)):
        process = subprocess.Popen([
            '/usr/bin/python3', os.path.join(args.backfill_base_path, 'backfill.py'),
            '--schedule_file', os.path.join(directory, 'schedule-%d.csv' % i),
            '--gpu_number', '%d' % (i*2),
            '--backfill_base_path', args.backfill_base_path,
            '--backend_url', args.backend_url,
            '--rsync_host', args.rsync_host],
            '--developer', args.developer],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy())
        processes.append(process)

    for i in range(len(subschedules)):
        stdout, stderr = processes[i].communicate()

        with open(os.path.join(directory, 'schedule-%d.stdout' % i), 'a') as f:
            f.write(stdout.decode('utf-8'))

        with open(os.path.join(directory, 'schedule-%s.stderr' % i), 'a') as f:
            f.write(stderr.decode('utf-8'))