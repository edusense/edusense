'''
This is new edusense pipeline, given a video, we generate tracking id first, and then shift to pose and face bb detection.
Once detected, we use gaze module to extract gaze information, and facial features network to extract facial features.

This is followed by all inferences from older video pipeline
'''

import os
import os.path as osp
import tempfile
from argparse import ArgumentParser
import mmcv
import numpy as np
import warnings
import cv2
from mmtrack.apis import inference_mot, init_model as init_tracking_model
from mmpose.apis import inference_top_down_pose_model, init_pose_model, vis_pose_result
from xtcocotools.coco import COCO
from mmpose.datasets import DatasetInfo
from GazeWrapper import GazeInference
import matplotlib.pyplot as plt
from FaceWrapper import RetinaFaceInference
from facenet_pytorch import InceptionResnetV1, MTCNN
from gaze.utils.inference import parse_roi_box_from_bbox
import torch
import tensorflow as tf
from multiprocessing import Queue, Process

# --------------------------------------------------
# configurations of dependencies

tf_version = tf.__version__
tf_major_version = int(tf_version.split(".", maxsplit=1)[0])
tf_minor_version = int(tf_version.split(".")[1])

if tf_major_version == 1:
    from keras.preprocessing import image
elif tf_major_version == 2:
    from tensorflow.keras.preprocessing import image

SOURCE_ROOT = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV2'
class_video_file = '/home/prasoon/video_analysis/mmtracking/first-10-min_5fps.mp4'
out_video_file = '/home/prasoon/video_analysis/mmtracking/first-10-min_5fps_pout.mp4'
OUT_ROOT = '/home/prasoon/video_analysis/edusenseV2compute/compute/videoV2/cache'

os.makedirs(OUT_ROOT, exist_ok=True)

run_config = {
    'track_config':f'{SOURCE_ROOT}/configs/mmlab/ocsort_yolox_x_crowdhuman_mot17-private-half.py',
    'track_checkpoint':f'{SOURCE_ROOT}/models/mmlab/ocsort_yolox_x_crowdhuman_mot17-private-half_20220813_101618-fe150582.pth',
    'pose_config':f'{SOURCE_ROOT}/configs/mmlab/hrnet_w32_coco_256x192.py',
    'pose_checkpoint':f'{SOURCE_ROOT}/models/mmlab/hrnet_w32_coco_256x192-c78dce93_20200708.pth',
    'device':'cuda:1',
    'kpt_thr':0.3,
    'video_fps':5,
}

def main():
    # read video file
    imgs = mmcv.VideoReader(class_video_file)
    IN_VIDEO = True
    fps = imgs.fps
    # build the model from a config file and a checkpoint file
    tracking_model = init_tracking_model(run_config['track_config'],
                                         run_config['track_checkpoint'],
                                         device=run_config['device'])
    # init pose model
    pose_model = init_pose_model(run_config['pose_config'], run_config['pose_checkpoint'],
                                 run_config['device'])
    pose_dataset = pose_model.cfg.data['test']['type']
    pose_dataset_info = pose_model.cfg.data['test'].get('dataset_info', None)
    config_pose = mmcv.Config.fromfile(run_config['pose_config'])
    h, w, _ = imgs[0].shape
    for component in config_pose.data.test.pipeline:
        if component['type'] == 'PoseNormalize':
            component['mean'] = (w // 2, h // 2, .5)
            component['max_value'] = (w, h, 1.)

    # init face boundingbox model and gaze model
    retinaface = RetinaFaceInference(device=torch.device(run_config['device']))
    gaze = GazeInference(device=run_config['device'])

    # init MTCNN model
    mtcnn = MTCNN(select_largest=False, post_process=False, device=run_config['device'])

    # Load facial recognition model
    resnet_vggface2_model = InceptionResnetV1(pretrained='vggface2', device=run_config['device']).eval()

    prog_bar = mmcv.ProgressBar(len(imgs))
    # test and show/save the images
    for i, img in enumerate(imgs):
        # img = imgs[i]
        track_results = inference_mot(tracking_model, img, frame_id=i)
        track_bboxes = track_results['track_bboxes'][0]
        # track_bboxes = track_bboxes[:,[0,1,3,2,4,5]]
        track_bboxes = [dict(bbox=x[1:],track_id=x[0]) for x in list(track_bboxes)]
        pose_results, _ = inference_top_down_pose_model(pose_model,
                                                     img,
                                                     track_bboxes,
                                                     format='xyxy',
                                                     dataset=pose_dataset,
                                                     dataset_info=pose_dataset_info)

        # det_bboxes = track_results['det_bboxes'][0]
        # # det_bboxes = det_bboxes[:,[0,2,1,3,4]]
        # det_bboxes = [dict(bbox=x) for x in list(det_bboxes)]
        # pose_results, _ = inference_top_down_pose_model(pose_model,
        #                                              img,
        #                                              det_bboxes,
        #                                              format='xyxy',
        #                                              dataset=pose_dataset,
        #                                              dataset_info=pose_dataset_info)


        tmp_out_file = os.path.join(f'/tmp/tmp.jpg')
        track_img = tracking_model.show_result(
            img,
            track_results,
            score_thr=0.4,
            show=False,
            wait_time=int(1000. / fps) if fps else 0,
            out_file=tmp_out_file,
            backend='cv2')

        pose_out_file = os.path.join(OUT_ROOT, f'{i:06d}.jpg')
        pose_out_img = vis_pose_result(
            pose_model,
            track_img,
            pose_results,
            dataset=pose_dataset,
            dataset_info=pose_dataset_info,
            kpt_score_thr=0.4,
            radius=4,
            thickness=4,
            show=False,
            out_file=pose_out_file)
        # print(type(track_results))

        # get face bounding box

        for body_pose_result in pose_results:
            body_bbox = body_pose_result['bbox']
            X_TL, Y_TL, X_BR, Y_BR = body_bbox[:4].astype(int)
            body_frame = img[Y_TL:Y_BR,X_TL:X_BR,:]
            faces, _ = retinaface.run(body_frame, frame_debug=None)
            mtcnn_faces, mtcnn_probs, landmarks = mtcnn.detect(body_frame, landmarks=True)
            # if mtcnn_faces is not None:
            #     mtcnn_faces[0][0] += X_TL
            #     mtcnn_faces[0][1] += Y_TL
            #     mtcnn_faces[0][2] += X_TL
            #     mtcnn_faces[0][3] += Y_TL
            #     # Get Gaze
            #     pred_gazes, _, mtcnn_points_2d, tvecs = gaze.run(img, mtcnn_faces, frame_debug=False)
            #     mtcnn_faces = ((int(mtcnn_faces[0][0]), (int(mtcnn_faces[0][1]))), (int(mtcnn_faces[0][2]), (int(mtcnn_faces[0][3]))))
            #     pose_out_img = cv2.rectangle(pose_out_img, mtcnn_faces[0], mtcnn_faces[1], color=(255, 255, 255), thickness=4)
            #     if len(mtcnn_points_2d) > 0:
            #         pose_out_img = cv2.arrowedLine(pose_out_img, tuple(mtcnn_points_2d[0][0]), tuple(mtcnn_points_2d[0][1]),
            #                                        color=(0, 255, 0), thickness=4)

            if faces.shape[0] > 0:
                faces[0][0] += X_TL
                faces[0][1] += Y_TL
                faces[0][2] += X_TL
                faces[0][3] += Y_TL
                # Get Gaze
                pred_gazes, _, points_2d, tvecs = gaze.run(img, faces, frame_debug=False)

                # Get facial embedding for given face.
                faces = faces[0][:4].astype(int)
                face_frame = img[faces[1]:faces[3],faces[0]:faces[2],:]
                target_size = (244,244)

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
                img_pixels = image.img_to_array(face_frame)  # what this line doing? must?
                img_pixels /= 255  # normalize input in [0, 1]

                # face_margin_lr,face_margin_tb =
                face_tensor = torch.from_numpy(img_pixels).permute(2, 1, 0).unsqueeze(0).to(run_config['device'])
                face_embedding = resnet_vggface2_model(face_tensor)[0].to('cpu').numpy()

                # faces = faces[0][:4]
                faces = ((int(faces[0]), (int(faces[1]))), (int(faces[2]), (int(faces[3]))))
                pose_out_img = cv2.rectangle(pose_out_img, faces[0], faces[1], color=(0,0,0),thickness=2)
                if len(points_2d)>0:
                    pose_out_img = cv2.arrowedLine(pose_out_img, tuple(points_2d[0][0]), tuple(points_2d[0][1]), color=(255, 0, 0), thickness=2)

        cv2.imwrite(pose_out_file,pose_out_img)
        prog_bar.update()
    mmcv.frames2video(OUT_ROOT, out_video_file, fps=fps, fourcc='mp4v')

if __name__ == '__main__':
    main()

