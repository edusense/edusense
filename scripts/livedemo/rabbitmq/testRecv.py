#!/usr/bin/env python
import pika, sys
import json
import os
import cv2
import numpy as np
import base64
from PIL import Image
from io import BytesIO as _BytesIO

BODY_PARTS = [(0,  "Nose"),
     (1,  "Neck"),
     (2,  "RShoulder"),
     (3,  "RElbow"),
     (4,  "RWrist"),
     (5,  "LShoulder"),
     (6,  "LElbow"),
     (7,  "LWrist"),
     (8,  "MidHip"),
     (9,  "RHip"),
     (10, "RKnee"),
     (11, "RAnkle"),
     (12, "LHip"),
     (13, "LKnee"),
     (14, "LAnkle"),
     (15, "REye"),
     (16, "LEye"),
     (17, "REar"),
     (18, "LEar"),
     (19, "LBigToe"),
     (20, "LSmallToe"),
     (21, "LHeel"),
     (22, "RBigToe"),
     (23, "RSmallToe"),
     (24, "RHeel"),
     (25, "Background")]
valid_idx_pairs = [(0,1),
                   (1,2),(2,3),(3,4),
                   (1,5),(5,6),(6,7),
                   (1,8),(8,9),(8,12),
                   (9,10),(10,11),(11,22),
                   (12,13),(13,14),(14,19),
                   (0,16),(16,18),
                   (0,15),(15,17),
                   (11,24),(23,22),
                   (14,21),(19,20)]


def annotate_image(im, ncols, nrows,body_kps):
    # add code for annotation hands only
    body_pts = [body_kps[i:i+3] for i in range(0,75,3)]
    for point in body_pts:
        if point[2]>0.7:
            im = cv2.circle(im, point[:2], radius=20,color=(255, 0, 0), thickness=20)
    for pair in valid_idx_pairs:
        if (body_pts[pair[0]][2] > 0.7) & (body_pts[pair[1]][2]>0.7):
            im = cv2.line(im,body_pts[pair[0]][:2],body_pts[pair[1]][:2],color=(0,0,255),thickness=20)
    return im


def main():
    credentials = pika.PlainCredentials('prasoon', 'edusenseMQ')
    parameters = pika.ConnectionParameters('sensei-delta.wv.cc.cmu.edu',
                                           5672,
                                           '/',
                                           credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

    result = channel.queue_declare(queue='livelogs', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(
        exchange='livedemo_exchange', queue=queue_name, routing_key='livedemo_test')

    def callback(ch, method, properties, frame_json):
        frame = json.loads(frame_json)
        thumbnail_binary = frame['thumbnail']['binary']
        ncols = frame['thumbnail']['originalCols']
        nrows = frame['thumbnail']['originalRows']
        # if not os.path.exists(f'{fileprefix}.png'):
        decoded = base64.b64decode(thumbnail_binary)
        buffer = _BytesIO(decoded)
        im = Image.open(buffer)
        im = cv2.resize(np.copy(im), (ncols, nrows))

        for i in range(len(frame['people'])):
            body_kps = frame['people'][i]['body']
            im = annotate_image(im, ncols, nrows, body_kps)
        im = cv2.resize(im, (int(ncols/4), int(nrows/4)))
        cv2.imshow("image", im)
        cv2.waitKey(1)
        return

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
