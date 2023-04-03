'''
Handler to process face embedding information from frame and face info
'''

import numpy as np
from datetime import datetime
from utils_computev3 import time_diff, get_logger
from copy import deepcopy
import cv2
from facenet_pytorch import InceptionResnetV1
import tensorflow as tf
import torch
import time
from queue import Empty as EmptyQueueException
tf_version = tf.__version__
tf_major_version = int(tf_version.split(".", maxsplit=1)[0])
tf_minor_version = int(tf_version.split(".")[1])


if tf_major_version == 1:
    from keras.preprocessing import image
elif tf_major_version == 2:
    from tensorflow.keras.preprocessing import image


def run_face_embedding_handler(face_embedding_input_queue, face_embedding_output_queue, session_config, logger_name):
    logger = get_logger(logger_name)
    # init face_embedding model
    facial_embedding_model = InceptionResnetV1(pretrained=session_config['face_embedding_model_name'],
                                               device=session_config['device']).eval()

    while True:
        wait_start = datetime.now()
        try:
            frame_number, video_frame, face_results = face_embedding_input_queue.get(timeout=0.1)
        except EmptyQueueException:
            time.sleep(0.5)
            continue
        wait_end = datetime.now()
        if video_frame is None:
            logger.info("Received none frame from input queue, exiting tracking handler.")
            break
        assert (type(video_frame) == np.ndarray) & (len(video_frame.shape) == 3)

        process_start = datetime.now()
        if face_results is not None:
            face_embedding_results = deepcopy(face_results)
            for body_index, face_result in enumerate(face_results):
                body_bbox = face_result['bbox']
                faces = face_result['face']
                X_TL, Y_TL, X_BR, Y_BR = body_bbox[:4].astype(int)
                if faces.shape[0] > 0:
                    faces[0][0] += X_TL
                    faces[0][1] += Y_TL
                    faces[0][2] += X_TL
                    faces[0][3] += Y_TL

                    # Get facial embedding for given face.
                    faces = faces[0][:4].astype(int)
                    face_frame = video_frame[faces[1]:faces[3], faces[0]:faces[2], :]
                    target_size = (244, 244)

                    if face_frame.shape[0] > 0 and face_frame.shape[1] > 0:
                        factor_0 = target_size[0] / face_frame.shape[0]
                        factor_1 = target_size[1] / face_frame.shape[1]
                        factor = min(factor_0, factor_1)

                        dsize = (int(face_frame.shape[1] * factor), int(face_frame.shape[0] * factor))
                        face_frame = cv2.resize(face_frame, dsize)

                        diff_0 = target_size[0] - face_frame.shape[0]
                        diff_1 = target_size[1] - face_frame.shape[1]

                        # Put the base image in the middle of the padded image
                        face_frame = np.pad(
                            face_frame,
                            (
                                (diff_0 // 2, diff_0 - diff_0 // 2),
                                (diff_1 // 2, diff_1 - diff_1 // 2),
                                (0, 0),
                            ),
                            "constant",
                        )
                    # double check: if target image is not still the same size with target.
                    if face_frame.shape[0:2] != target_size:
                        face_frame = cv2.resize(face_frame, target_size)

                    # normalizing the image pixels
                    video_frame_pixels = face_frame.astype(np.float32)  # what this line doing? must?
                    video_frame_pixels /= 255  # normalize input in [0, 1]
                    face_tensor = torch.from_numpy(video_frame_pixels).permute(2, 1, 0).unsqueeze(0).to(
                        session_config['device'])
                    face_embedding = facial_embedding_model(face_tensor)[0].to('cpu').detach().numpy()
                    face_results[body_index].update({
                        'face_embedding':face_embedding
                    })

            face_embedding_output_queue.put((frame_number, 'face_embedding', face_embedding_results))

        process_end = datetime.now()

        logger.info(
            f"Frame: {frame_number}, {time_diff(wait_start, wait_end):.3f} secs | {time_diff(process_start, process_end):.3f} secs")

    return None
