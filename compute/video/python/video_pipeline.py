# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.

import argparse
import base64
import datetime
from datetime import timedelta
from datetime import datetime
import json
import queue
import os
import socket
import struct
import sys
import threading
import time
import traceback
import sys
import cv2
import numpy
import requests
import deepgaze
import get_time as gt
from get_time import time_diff
import math
import logging
from logging.handlers import WatchedFileHandler
import traceback

import gaze_3d
from centroidtracker import *
from headpose import *
from render import *
from process import *

default_schema = "edusense-video"
default_keyword = "edusense-keyword"
RTSP = False
skipframe = 0


class SocketReaderThread(threading.Thread):
    def __init__(self, queue, server_address, keep_frame_number, logger_pass, logging_dict,
                 profile=False):
        threading.Thread.__init__(self)
        self.queue = queue
        self.server_address = server_address
        self.keep_frame_number = keep_frame_number
        self.frame_number = 0
        self.profile = profile
        self.logger_base = logger_pass.getChild('reader_thread')
        self.logging_dict = logging_dict
        self.logger = logging.LoggerAdapter(self.logger_base, logging_dict)
        self.logger.info("Constructed Socker Reader Thread.")

    def start(self):
        logger = self.logger
        sock = None
        logger.info("Bind Socket address to receive openpose frames")
        if isinstance(self.server_address, tuple):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            # Make sure the socket does not already exist
            try:
                os.unlink(self.server_address)
            except:
                if os.path.exists(self.server_address):
                    logger.info("Socket already exists")
                    raise

            # create a unix domain socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # bind the socket to the port
        sock.bind(self.server_address)
        logger.info("Bound socket to port")

        # listen for incoming connections
        logger.info("Start listening to openpose socket.")
        sock.listen(1)

        # wait for incoming connection
        logger.info("Waiting for incoming connections.")
        self.conn, self.client_address = sock.accept()

        # mark this is running
        logger.info("Mark socket reader thread running...")
        self.is_running = True

        # start
        super(SocketReaderThread, self).start()

    def stop(self):
        self.logger.info("Mark socket reader thread stopped running...")
        self.is_running = False

    def run(self):
        logger = self.logger
        try:
            # receive data in small chunks
            logger.info("Receive data in small chunks")
            while self.is_running:
                t_socket_read_start = datetime.now()
                logger.info(f"Waiting at for next packet at {t_socket_read_start.strftime('%Y-%m-%d %H:%M:%S')}")
                # Read size of the payload
                size_data = self.conn.recv(4)
                msg_len = struct.unpack('=I', size_data)[0]
                logger.info(f"Next Packet Size:{str(msg_len)}")
                # termination signal
                if msg_len == 0:
                    logger.info(f"Zero length packet received, exiting reader loop")
                    break

                chunks = []
                bytes_recvd = 0

                # Read payload
                while bytes_recvd < msg_len:
                    chunk = self.conn.recv(min(msg_len - bytes_recvd, 1048576))
                    if chunk == b'':
                        logger.error("Socket connection broken. Throwing runtime error")
                        raise RuntimeError("socket connection broken")

                    chunks.append(chunk)
                    bytes_recvd = bytes_recvd + len(chunk)

                msg = b''.join(chunks)
                self.frame_number += 1
                numbered_msg = (None, msg) if self.keep_frame_number \
                    else (self.frame_number, msg)
                logger.info("Read Payload for frame %d in %.3f secs", self.frame_number,
                            time_diff(t_socket_read_start, datetime.now()))

                # if self.profile:
                #     logger.info('socket_read,%f' %
                #                 (time.time() - socket_read_start_time))

                if self.queue is not None:
                    self.queue.put(numbered_msg, True, None)
                    logger.info("----Posted payload to queue----")

        except Exception as e:
            is_running = False
            logger.info("Exception thrown", traceback.format_exc())
            traceback.print_exc(file=sys.stdout)
        finally:
            self.conn.close()


class ConsumerThread(threading.Thread):
    def __init__(self, input_queue, process_real_time, process_gaze, gaze_3d, channel,
                 area_of_interest, fps, start_date, start_time, logger_pass, logging_dict, backend_params=None,
                 file_params=None,
                 profile=False, skipframe=0):
        threading.Thread.__init__(self)
        self.input_queue = input_queue
        self.process_real_time = process_real_time
        self.channel = channel
        self.counter = 0;
        self.skipframe = skipframe
        self.fps = fps;
        self.currentframe = 1;
        self.start_date = start_date;
        self.start_time = start_time;
        if area_of_interest is not None:
            self.area_of_interest = np.array(area_of_interest).reshape((-1, 1, 2))
        else:
            self.area_of_interest = None

        # Initialize file posting
        self.file_params = file_params
        if file_params is not None and file_params['video'] is not None:
            self.video_out = cv2.VideoWriter(
                os.path.join(self.file_params['base_dir'],
                             file_params['video']),
                cv2.VideoWriter_fourcc(*'XVID'), 5.0, (1920, 1080))
        else:
            self.video_out = None

        # Initialize backend posting
        self.backend_params = backend_params

        # Initialize centroid tracker
        self.centroid_tracker = CentroidTracker()
        self.centroid_time_live = 10
        self.centroid_initialize_time = 1
        self.state = {
            'prev_objects': None,
            'prev_pose': None,
            'current_pose': None,
            'prev_time': None
        }

        # configure machine learning
        self.process_gaze = process_gaze
        self.gaze_3d = gaze_3d

        self.profile = profile

        self.logger_base = logger_pass.getChild('consumer_thread')
        self.logger = logging.LoggerAdapter(self.logger_base, logging_dict)
        self.logger.info("Constructed Consumer Thread.")

    def start(self):
        self.input_queue = self.input_queue
        self.is_running = True
        if self.process_real_time:
            self.logger.info("Starting Consumer Thread with real time setting.")
        else:
            self.logger.info("Starting Consumer Thread with back-filling setting.")
        super(ConsumerThread, self).start()

    def run(self):
        logger = self.logger
        while self.is_running:
            if self.process_real_time:
                numbered_datum = None
                cnt = 0
                logger.info("Waiting on frame data from queue")
                try:
                    while True:
                        numbered_datum_temp = self.input_queue.get_nowait()
                        numbered_datum = numbered_datum_temp

                        cnt += 1
                except Exception:
                    if numbered_datum is None:
                        continue

                # process data
                logger.info("Starting to process frame")
                raw_image, frame_data = self.process_frame(numbered_datum)

                if not RTSP:
                    time = int(frame_data['frameNumber'] / self.fps)
                    frame_data['timestamp'] = self.start_date + 'T' + str(
                        self.start_time + timedelta(seconds=time)) + 'Z'
                logger.info(
                    f"Processed Frame {str(frame_data['frameNumber'])} from timestamp {str(frame_data['timestamp'])}")
                logger.info('...........................')
                # logger.info(frame_data['timestamp'])
                # logger.info(frame_data['frameNumber'])
                # logger.info('...........................')

                # post data
                logger.info("Starting to post frame results")
                self.post_frame(raw_image, frame_data)

                for i in range(cnt):
                    self.input_queue.task_done()
            else:
                t_skipframe_start = datetime.now()
                while self.currentframe < self.skipframe:
                    self.currentframe = self.currentframe + 1
                    self.input_queue.get()
                    self.input_queue.task_done()
                t_skipframe_end = datetime.now()
                logger.info("Skipping %d Frames to match expected FPS in %.3f secs", self.skipframe,
                            time_diff(t_skipframe_start, t_skipframe_end))
                self.currentframe = 1
                logger.info("Starting to process frame")
                raw_image, frame_data = self.process_frame(self.input_queue.get())
                time = float(frame_data['frameNumber'] / self.fps)
                frame_data['timestamp'] = self.start_date + 'T' + str(
                    self.start_time + timedelta(seconds=time)) + 'Z'
                logger.info(f"Processed Frame {str(frame_data['frameNumber'])} from timestamp {str(frame_data['timestamp'])}")
                logger.info('...........................')
                # logger.info(frame_data['timestamp'])
                # logger.info(frame_data['frameNumber'])
                # logger.info('...........................')

                # post data
                logger.info("Starting to post frame results")
                self.post_frame(raw_image, frame_data)
                self.input_queue.task_done()

    def stop(self):
        self.input_queue.join()
        self.is_running = False

        if self.video_out is not None:
            self.video_out.release()

    def process_frame(self, numbered_datum):
        logger = self.logger

        t_process_frame_start = datetime.now()
        logger.info("===Start Processing New Frame===")
        start_time = time.time()
        frame_data = None
        raw_image = None

        try:
            json_time = 0
            featurization_time = 0
            thumbnail_time = 0
            interframe_time = 0
            t_json_start = datetime.now()
            frame_number, datum = numbered_datum

            frame_data = json.loads(datum.decode('utf-8'))
            if frame_number is not None:
                frame_data['frameNumber'] = frame_number
                logger.info(f"Got frame number %d", frame_number)

            t_json_end = datetime.now()
            json_time = time_diff(t_json_start, t_json_end)
            logger.info("Loaded json data in %.3f secs", json_time)

            image_rows = 0
            image_cols = 0
            has_raw_image = "rawImage" in frame_data.keys()
            has_thumbnail = "thumbnail" in frame_data.keys()
            raw_image = None

            if has_raw_image:
                image_rows = frame_data["rawImage"]["rows"]
                image_cols = frame_data["rawImage"]["columns"]

                image_bytes = base64.standard_b64decode(
                    frame_data["rawImage"]["binary"])
                image_array = numpy.frombuffer(image_bytes, dtype=numpy.uint8)
                raw_image = numpy.reshape(
                    image_array, (image_rows, image_cols, 3))
                logger.info(f"Got raw image with %d rows, and %d cols", image_rows, image_cols)

                del frame_data["rawImage"]

                if not has_thumbnail:
                    # logger.info("Start creating thumbnail")
                    t_thumbnail_start = datetime.now()
                    resized_image = cv2.resize(raw_image, (240, 135))
                    r, buf = cv2.imencode('.jpg', resized_image, [
                        int(cv2.IMWRITE_JPEG_QUALITY), 50])
                    frame_data['thumbnail'] = {
                        'binary': base64.standard_b64encode(buf).decode('ascii'),
                        'originalCols': image_cols,
                        'originalRows': image_rows
                    }

                    t_thumbnail_end = datetime.now()
                    thumbnail_time = time_diff(t_thumbnail_start, t_thumbnail_end)
                    logger.info("Finish creating thumbnail in %.3f secs", thumbnail_time)

            elif has_thumbnail:
                image_rows = frame_data["thumbnail"]["originalRows"]
                image_cols = frame_data["thumbnail"]["originalColumns"]

            # Featurization
            logger.info("--Start frame featurization--")
            t_featurization_start = datetime.now()
            # featurization_start_time = time.time()

            # extract key points
            bodies = frame_data['people']
            rects = []
            person_poses = []
            logger.info(f"Count of bodies found in frame: {str(len(bodies))}")
            if self.area_of_interest is not None:
                bodies = list(map(lambda b: get_pts_of_interest_from_person(b, self.area_of_interest), bodies))
                logger.info(f"Removed bodies outside area of interest in frame")
            bodies = list(filter(lambda b: check_body_pts(b['body']), bodies))

            logger.info(f"Count of bodies found in area of interest: {str(len(bodies))}")
            t_prepare_interframe_start = datetime.now()

            for body_idx, body in enumerate(bodies):
                body_keypoints = body["body"]
                face_keypoints = body["face"] if "face" in body.keys() else None

                # prune body keypoints
                body_keypoints = prune_body_pts(body_keypoints)
                body["body"] = body_keypoints
                pose = get_pose_pts(body_keypoints)
                body['inference'] = {
                    'posture': {},
                    'face': {},
                    'head': {}
                }
                # prepare inter-frame tracking
                box = get_pose_box(pose)
                rects.append(box.astype("int"))
                person_poses.append(pose)

            t_prepare_interframe_end = datetime.now()
            logger.info("Pruned body kps and prepare for interframe processing in %.3f secs",
                        time_diff(t_prepare_interframe_start, t_prepare_interframe_end))

            # Interframe
            logger.info("Start interframe processing")
            t_run_interframe_start = datetime.now()
            tracking_id = None

            objects, poses = self.centroid_tracker.update(rects, person_poses)

            for body in bodies:
                body_keypoints = body["body"]
                pose = get_pose_pts(body_keypoints)
                for (objectID, person_pose) in poses.items():
                    if pose[1][0] == person_pose[1][0] and pose[1][1] == person_pose[1][1]:
                        body['inference']['trackingId'] = objectID + 1
                        if self.video_out is not None or (self.file_params is not None and self.file_params['image']):
                            text = "ID {}".format(objectID)
                            cv2.putText(raw_image, text, (person_pose[1][0] - 10, person_pose[1][1] - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            cv2.circle(
                                raw_image, (person_pose[1][0], person_pose[1][1]), 4, (0, 255, 0), -1)
                        break

            t_run_interframe_end = datetime.now()
            interframe_time = time_diff(t_run_interframe_start, t_run_interframe_end)
            logger.info("Finish interframe processing in %.3f secs", interframe_time)
            # featurization_start_time =time.time()

            if self.channel == 'instructor':
                start_time = time.time()
                y_min = None
                instructor_body_track = None
                for (objectID, person_pose) in poses.items():
                    if y_min is None and person_pose[1][1] > 0 and person_pose[1][0] > 0:
                        y_min = person_pose[1][1]
                        instructor_body_track = person_pose
                    else:
                        if person_pose[1][1] < y_min and person_pose[1][1] > 0 and person_pose[1][0] > 0:
                            y_min = person_pose[1][1]
                            instructor_body_track = person_pose

                new_bodies = []
                if instructor_body_track is not None:
                    for body in bodies:
                        body_keypoints = body["body"]
                        pose = get_pose_pts(body_keypoints)
                        if pose[1][0] == instructor_body_track[1][0] and pose[1][1] == instructor_body_track[1][1]:
                            new_bodies.append(body)
                            break
                bodies = new_bodies
                logger.info("Instructor Channel, selected instructor based on tracking id in %.3f secs",
                            time.time() - start_time)

            body_time_profile = {}
            for body_idx, body in enumerate(bodies):

                body_time_profile[body_idx] = {
                    'trackingId': str(body.get('inference', {}).get('trackingId', 'notFound'))
                }  # profile time for each person

                start_time = time.time()
                body_keypoints = body["body"]
                face_keypoints = body["face"] if "face" in body.keys(
                ) else None
                pose = get_pose_pts(body_keypoints)
                body_time_profile[body_idx]['get_keypoints'] = round(time.time() - start_time, 3)

                start_time = time.time()
                # face orientation
                faceOrientation = None
                faceOrientation = get_facing_direction(pose)
                body_time_profile[body_idx]['get_face_orient'] = round(time.time() - start_time, 3)

                # Sit stand
                start_time = time.time()
                sit_stand, color_stand, pts = predict_sit_stand(body_keypoints)
                if self.video_out is not None or (self.file_params is not None and self.file_params['image']):
                    cv2.putText(raw_image, sit_stand, (int(pts[1][0]) - 10, int(
                        pts[1][1]) + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color_stand, 2, cv2.LINE_AA)
                body_time_profile[body_idx]['get_sit_stand'] = round(time.time() - start_time, 3)

                # Armpose
                start_time = time.time()
                armpose, color_pose, pts = predict_armpose(body_keypoints)
                if self.video_out is not None or (self.file_params is not None and self.file_params['image']):
                    cv2.putText(raw_image, armpose, (int(
                        pts[1][0]) - 10, int(pts[1][1]) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color_pose, 2,
                                cv2.LINE_AA)
                    raw_image = render_pose_draw(
                        [pose], raw_image, color_pose, color_stand)
                body_time_profile[body_idx]['get_armpose'] = round(time.time() - start_time, 3)

                # Mouth
                start_time = time.time()
                mouth = None
                smile = None
                if face_keypoints is not None:
                    mouth, _, smile, _ = predict_mouth(face_keypoints)

                tvec = None
                yaw = None
                pitch = None
                roll = None
                gaze_vector = None
                face = get_face(pose)
                body_time_profile[body_idx]['get_smile'] = round(time.time() - start_time, 3)

                start_time = time.time()
                if (self.gaze_3d):
                    if face is not None:
                        bboxes = [
                            face[0][0], face[0][1], face[1][0], face[1][1]
                        ]
                        bboxes = np.array(bboxes)
                        bboxes = bboxes.reshape(-1, 4)
                        # print(face)
                        # logger.info('.......')
                        tvec, rvec, point_2d, face = gaze_3d.get_3d_pose(raw_image, bboxes,
                                                                         face)  ##TODO-: change the face variablr
                        # logger.info(point_2d)
                        tvec = tvec.tolist()
                        rvec = rvec.tolist()
                        # print(face)
                        if point_2d[0][0] is not None:
                            gaze_vector = point_2d

                        pitch, roll, yaw = rvec

                        if pitch is not None:
                            # convert to degree
                            pitch = (pitch * 180) / math.pi
                            roll = (roll * 180) / math.pi
                            yaw = (yaw * 180) / math.pi
                    body_time_profile[body_idx]['get_gaze_3d'] = round(time.time() - start_time, 3)
                elif (self.process_gaze):
                    tvec = get_3d_head_position(pose, raw_image.shape)
                    # face box
                    if face is not None:
                        face_crop = raw_image[face[0][1]:face[1][1], face[0][0]:face[1][0]]
                        if face_crop.shape[0] >= 64 and face_crop.shape[1] >= 64:
                            yaw, pitch, roll, gaze_start, gaze_stop = get_head_pose_vector(
                                face_crop, face)
                            yaw = yaw.flatten().tolist()[0]
                            pitch = pitch.flatten().tolist()[0]
                            roll = roll.flatten().tolist()[0]
                            gaze_vector = [gaze_start, gaze_stop]
                            cv2.line(raw_image, gaze_start,
                                     gaze_stop, (255, 255, 255), 2)
                    body_time_profile[body_idx]['get_gaze_old'] = round(time.time() - start_time, 3)

                start_time = time.time()
                if armpose is not None:
                    body['inference']['posture']['armPose'] = armpose
                if sit_stand is not None:
                    body['inference']['posture']['sitStand'] = sit_stand
                if face is not None:
                    body['inference']['face']['boundingBox'] = face
                if mouth is not None:
                    body['inference']['face']['mouth'] = mouth
                if smile is not None:
                    body['inference']['face']['smile'] = smile
                if yaw is not None:
                    body['inference']['head']['yaw'] = yaw
                if pitch is not None:
                    body['inference']['head']['pitch'] = pitch
                if roll is not None:
                    body['inference']['head']['roll'] = roll
                if faceOrientation is not None:
                    body['inference']['face']['orientation'] = faceOrientation
                if gaze_vector is not None:
                    body['inference']['head']['gazeVector'] = gaze_vector
                if tvec is not None:
                    body['inference']['head']['translationVector'] = tvec

                body_time_profile[body_idx]['fill_inferences'] = round(time.time() - start_time, 3)

            # Acceleration
            prev_objects = self.state['prev_objects']
            previous_time = self.state['prev_time']
            current_time = time.time()

            for body_idx, body in enumerate(bodies):
                start_time = time.time()
                body_keypoints = body["body"]
                pose = get_pose_pts(body_keypoints)
                for (objectID, person_pose) in poses.items():
                    if prev_objects is not None:
                        for (objectID_2, person_pose2) in prev_objects.items():
                            if objectID == objectID_2:
                                if person_pose2[1][0] != 0 and person_pose2[1][1] != 0 and person_pose[1][0] != 0 and \
                                        person_pose[1][1] != 0:
                                    if pose[1][0] == person_pose[1][0] and pose[1][1] == person_pose[1][1]:
                                        centroid_delta = []
                                        if previous_time is not None and float(
                                                current_time - previous_time) < self.centroid_time_live:
                                            centroid_delta = [
                                                person_pose[1][0] - person_pose2[1][0],
                                                person_pose[1][1] - person_pose2[1][1]]
                                            if self.video_out is not None or (
                                                    self.file_params is not None and self.file_params['image']):
                                                cv2.arrowedLine(raw_image, (person_pose2[1][0], person_pose2[1][1]), (
                                                    person_pose[1][0], person_pose[1][1]), (255, 255, 255), 2,
                                                                cv2.LINE_AA)

                                        arm_delta = None
                                        draw_arm_index = [3, 4, 6, 7]
                                        for i in draw_arm_index:
                                            delta = (0, 0)
                                            if person_pose2[i][0] == 0 or person_pose2[i][1] == 0 or person_pose[i][
                                                0] == 0 or person_pose[i][1] == 0:
                                                delta = (0, 0)
                                            elif previous_time is not None and float(
                                                    current_time - previous_time) < self.centroid_time_live:
                                                delta = (
                                                    person_pose[i][0] - person_pose2[i][0],
                                                    person_pose[i][1] - person_pose2[i][1])
                                                if self.video_out is not None or (
                                                        self.file_params is not None and self.file_params['image']):
                                                    cv2.arrowedLine(raw_image, (person_pose2[i][0], person_pose2[i][1]),
                                                                    (
                                                                        person_pose[i][0], person_pose[i][1]),
                                                                    (255, 255, 0), 2, cv2.LINE_AA)
                                            if arm_delta is None:
                                                arm_delta = [delta]
                                            else:
                                                arm_delta.append(delta)

                                        body['inference']['posture']['centroidDelta'] = centroid_delta
                                        body['inference']['posture']['armDelta'] = arm_delta
                body_time_profile[body_idx]['get_centroid_arm_delta'] = round(time.time() - start_time, 3)

            t_featurization_end = datetime.now()

            featurization_time = time_diff(t_featurization_start, t_featurization_end)
            logger.info("Finish featurization in %.3f secs", featurization_time)

            # Log body level information
            for body_idx in body_time_profile.keys():
                body_head_str = f"TrackingID: {body_time_profile[body_idx]['trackingId']}"
                body_time_str = ','.join(
                    [f"{k}:{body_time_profile[body_idx][k]}" for k in body_time_profile[body_idx].keys() if
                     not (k == 'trackingId')])
                logger.info(f"{body_head_str} | {body_time_str}")

            if previous_time is None or float(current_time - previous_time) > self.centroid_initialize_time:
                self.state['prev_time'] = current_time
                self.state['prev_objects'] = poses.copy()

            frame_data['channel'] = self.channel
            frame_data['people'] = bodies

            if self.profile:
                logger.info('json,%f' % json_time)
                logger.info('featurization,%f' % featurization_time)
                logger.info('thumbnail,%f' % thumbnail_time)
                logger.info('interframe,%f' % interframe_time)

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
        t_process_frame_end = datetime.now()
        logger.info("Finished processing frame in %.3f secs", time_diff(t_process_frame_start, t_process_frame_end))
        return raw_image, frame_data

    def post_frame(self, raw_image, frame_data):
        if self.file_params is not None:
            self.post_frame_to_file(raw_image, frame_data)

        if self.backend_params is not None:
            self.post_frame_to_backend(frame_data)

    def post_frame_to_file(self, raw_image, frame_data):
        logger = self.logger
        logger.info("Starting to post frame to file")
        t_post_file_start = datetime.now()
        if frame_data is not None:
            try:
                file_post_start_time = time.time()
                if self.area_of_interest is not None:
                    cv2.drawContours(raw_image, [self.area_of_interest], -1, (0, 0, 255), 5)

                if self.file_params['image'] and raw_image is not None:
                    path = os.path.join(self.file_params['base_dir'], '%d.%s.jpg' % (
                        frame_data['frameNumber'], self.channel))
                    cv2.imwrite(path, cv2.resize(raw_image, (1920, 1080)))

                if self.video_out is not None and raw_image is not None:
                    self.video_out.write(cv2.resize(raw_image, (1920, 1080)))

                if self.file_params['json']:
                    path = os.path.join(self.file_params['base_dir'], '%d.%s.json' % (
                        frame_data['frameNumber'], self.channel))
                    with open(path, 'w') as f:
                        json.dump(frame_data, f)

                file_post_time = time.time() - file_post_start_time

                if self.profile:
                    logger.info('file_posting,%f' % file_post_time)

            except Exception as e:
                logger.info("Exception thrown: ",traceback.format_exc())
                traceback.print_exc(file=sys.stdout)
        t_post_file_end = datetime.now()
        logger.info("Completed file posting in %.3f secs", time_diff(t_post_file_start, t_post_file_end))

    def post_frame_to_backend(self, frame_data):
        logger = self.logger
        logger.info("Starting to post frame to backend")
        t_post_backend_start = datetime.now()
        if frame_data is not None:
            # if frame_data['channel'] == 'student':
            #    print frame_data
            try:
                db_post_start_time = time.time()
                resp = requests.post(self.backend_params['url'],
                                     headers=self.backend_params['headers'],
                                     json={'frames': [frame_data]})
                if (resp.status_code != 200 or
                        'success' not in resp.json().keys() or
                        not resp.json()['success']):
                    raise RuntimeError(resp.text)

                db_post_time = time.time() - db_post_start_time

                if self.profile:
                    logger('db_posting,%f' % db_post_time)

            except Exception as e:
                traceback.print_exc(file=sys.stdout)
        t_post_backend_end = datetime.now()
        logger.info("Completed backend posting in %.3f secs", time_diff(t_post_backend_start, t_post_backend_end))



def run_pipeline(server_address, time_duration, process_real_time,
                 process_gaze, gaze_3d, keep_frame_number, channel, area_of_interest,
                 fps, start_date, start_time, root_logger, logging_dict, backend_params=None,
                 file_params=None, profile=False, skipframe=0):
    # initialize loggers
    logger_base = root_logger.getChild('run_pipeline')
    logger = logging.LoggerAdapter(logger_base, logging_dict)

    # initialize queues
    q = None
    if process_real_time:
        q = queue.LifoQueue()
    else:
        # queue size 1 for now
        q = queue.Queue(1)

    # initialize socket reader thread, this thread multiplexes multiple queues
    # for the sake of simplicity, it is one producer, multiple consumer design
    reader_thread = SocketReaderThread(q, server_address, keep_frame_number, logger_base, logging_dict,
                                       profile)

    # initialize video consumers
    consumer_thread = ConsumerThread(q, process_real_time, process_gaze, gaze_3d,
                                     channel, area_of_interest, fps, start_date, start_time, logger_base, logging_dict,
                                     backend_params, file_params, profile, skipframe)

    # start downstream (consumers)
    t_consumer_thread_start = datetime.now()
    logger.info("Starting Consumer Thread")
    consumer_thread.start()

    # then, start upstream (producer)
    t_reader_thread_start = datetime.now()
    logger.info("Starting Reader Thread")
    reader_thread.start()

    # run forever if duration is negative
    if time_duration < 0:
        # this only works python 3.2+ and on linux
        # threading.Event().wait()

        # wait for reader to finish
        reader_thread.join()
        t_reader_thread_end = datetime.now()
        logger.info("Finished Reader Thread in %.3fs", time_diff(t_reader_thread_start, t_reader_thread_end))

        # wait for consumer thread to finish
        consumer_thread.stop()
        consumer_thread.join()
        t_consumer_thread_end = datetime.now()
        logger.info("Finished Consumer Thread in %.3fs", time_diff(t_consumer_thread_start, t_consumer_thread_end))

    else:  # shutdown after time_duration seconds
        time.sleep(time_duration)

        # terminate upstream
        reader_thread.stop()

        # join the upstream
        reader_thread.join()
        t_reader_thread_end = datetime.now()
        logger.info("Finished Reader Thread in %.3fs", time_diff(t_reader_thread_start, t_reader_thread_end))

        # terminate downstream
        consumer_thread.stop()

        # join the downstream
        consumer_thread.join()
        t_consumer_thread_end = datetime.now()
        logger.info("Finished Consumer Thread in %.3fs", time_diff(t_consumer_thread_start, t_consumer_thread_end))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='EduSense video computation backend')
    parser.add_argument('--video', dest='video', type=str, nargs='?',
                        help='video address', required=True)
    parser.add_argument('--video_sock', dest='video_sock', type=str, nargs='?',
                        help='EduSense video server address')
    parser.add_argument('--tcp_host', dest='tcp_host', type=str, nargs='?',
                        help='EduSense video server TCP host')
    parser.add_argument('--tcp_port', dest='tcp_port', type=int, nargs='?',
                        help='EduSense video server TCP port')
    parser.add_argument('--backend_url', dest='backend_url', type=str,
                        nargs='?', help='Edusense backend storage url '
                                        '(hostport)')
    parser.add_argument('--file_output_dir', dest='file_output_dir', type=str,
                        nargs='?')
    parser.add_argument('--session_id', dest='session_id', type=str, nargs='?',
                        help='EduSense session id')
    parser.add_argument('--schema', dest='schema', type=str, nargs='?',
                        default=default_schema, help='EduSense schema')
    parser.add_argument('--time_duration', dest='time_duration', type=int,
                        nargs='?', default=60, help='Session duration')
    parser.add_argument('--process_real_time', dest='process_real_time',
                        action='store_true', help='if set, skip frames to keep'
                                                  'realtime')
    parser.add_argument('--process_gaze', dest='process_gaze',
                        action='store_true', help='if set, process gaze')
    parser.add_argument('--gaze_3d', dest='gaze_3d',
                        action='store_true', help='if set, process new gaze')
    parser.add_argument('--keep_frame_number', dest='keep_frame_number',
                        action='store_true', help='if set, keep frame number '
                                                  'given by openpose, otherwise issue new frame number')
    parser.add_argument('--area_of_interest', dest='area_of_interest',
                        type=int, nargs='+', help='process bodies in certain '
                                                  'area. --area_of_interest <x1> <y1> <x2> <y2>')
    parser.add_argument('--profile', dest='profile', action='store_true',
                        help='if set, profile performance')
    parser.add_argument('--backfillFPS', dest='backfillFPS', type=float,
                        help='frames per sec for backfilling', default=0)
    parser.add_argument('--instructor', dest='instructor', action='store_true',
                        help='if set, run instructor view')
    parser.add_argument('--video_out', dest='video_out', type=str, nargs='?')
    parser.add_argument('--image_out', dest='image_out', action='store_true',
                        help='if set, save decorated image files')
    parser.add_argument('--json_out', dest='json_out', action='store_true',
                        help='if set, save json files')
    parser.add_argument('--use_unix_socket', dest='use_unix_socket',
                        action='store_true', help='if set, use unix socket')
    args = parser.parse_args()

    logger_master = logging.getLogger('video_pipeline')
    logger_master.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s | %(process)s, %(thread)d | %(video_name)s | %(name)s | %(levelname)s | %(message)s')
    logging_dict = {
        'video_name': args.video.split("/")[-1]
    }

    ## Add core logger handler
    video_name = args.video.split("/")[-1].split(".")[0]
    log_file = f"/tmp/{video_name}.log"
    core_logging_handler = WatchedFileHandler(log_file)
    core_logging_handler.setFormatter(formatter)
    logger_master.addHandler(core_logging_handler)

    ## Add stdout logger handler
    if args.backend_url is None:
        console_log = logging.StreamHandler()
        console_log.setLevel(logging.DEBUG)
        console_log.setFormatter(formatter)
        logger_master.addHandler(console_log)

    logger = logging.LoggerAdapter(logger_master, logging_dict)

    channel = 'instructor' if args.instructor else 'student'
    logger.info("Channel: %s", channel)

    if args.area_of_interest is not None:
        if len(args.area_of_interest) % 2 == 1 or len(args.area_of_interest) < 6:
            logger.warning(
                'for area of interest, you should put x, y pairs: suppied {}'.format(len(args.area_of_interest)))

    ## if log volume is mounted
    if channel == 'instructor':
        File = '/tmp/back_video.txt'
    else:
        File = '/tmp/front_video.txt'
    try:
        log = open(File, 'w')
    except:
        log = open('video_log.txt', 'w')

    if 'rtsp' in args.video:
        logger.info("RSTP is set to true.")
        RTSP = True

    ###extract starting time #####
    if (RTSP):
        log.write(args.video + " timestamp log\nUsing RTSP\n")
        logger.info(args.video + " timestamp log\nUsing RTSP\n")
        fps = None
        start_time = None
        start_date = None
    else:
        log.write(args.video + " timestamp log\n")
        logger.info(args.video + " timestamp log\n")
        fps, start_date, start_time = gt.extract_time(args.video, log)
        logger.info(
            f"Extracted time information, FPS:{str(fps)}, start date:{str(start_date)},start time:{str(start_time)}")
        log.close()
        ##############################
        if fps == None or fps == 0:
            logger.error("either video address not valid or not able to extract the fps")
            logger.error("Exiting Video Pipeline")
            sys.exit(1)

    if args.backfillFPS != 0:
        skipframe = int(float(fps) / float(args.backfillFPS)) - 1

    if skipframe < 0:
        skipframe = 0

    # setup backend params
    logger.info("Setting backend parameters for posting frame data.")
    backend_params = None
    app_username = os.getenv("APP_USERNAME", "")
    app_password = os.getenv("APP_PASSWORD", "")
    if args.backend_url is not None and args.session_id is not None:
        cred = '{}:{}'.format(app_username, app_password).encode('ascii')
        encoded_cred = base64.standard_b64encode(cred).decode('ascii')

        backend_params = {
            'url': ('https://%s/sessions/%s/video/frames/%s/%s/' %
                    (args.backend_url, args.session_id, args.schema, channel)),
            'headers': {
                'Authorization': 'Basic {}'.format(encoded_cred),
                'Content-Type': 'application/json'}
        }

    # setup file params
    file_params = None
    if args.file_output_dir is not None:
        logger.info("Setting file parameters for posting frame data.")
        file_params = {
            'base_dir': args.file_output_dir,
            'json': args.json_out,
            'image': args.image_out,
            'video': args.video_out
        }

    profile = args.profile
    server_address = (args.video_sock
                      if args.use_unix_socket
                      else (args.tcp_host, args.tcp_port))
    logger.info("Initiating video pipeline run...")
    t_pipeline_start = datetime.now()
    run_pipeline(server_address, args.time_duration, args.process_real_time,
                 args.process_gaze, args.gaze_3d, args.keep_frame_number, channel,
                 args.area_of_interest, fps, start_date, start_time, logger_master, logging_dict, backend_params,
                 file_params, profile, skipframe)
    t_pipeline_end = datetime.now()
    logger.info("Finished running pipeline in %.3f secs", time_diff(t_pipeline_start, t_pipeline_end))
