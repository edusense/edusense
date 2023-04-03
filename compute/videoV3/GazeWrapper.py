import gaze

import torch
import torchvision.transforms as transforms
import gaze.mobilenet_v1 as mobilenet_v1
import numpy as np
import cv2
from gaze.utils.ddfa import ToTensorGjz, NormalizeGjz
import torch.backends.cudnn as cudnn
from gaze.utils.estimate_pose import parse_pose
from gaze.utils.inference import predict_68pts, draw_landmarks, calc_hypotenuse, crop_img
from gaze.utils.inference import parse_roi_box_from_landmark, parse_roi_box_from_bbox
from gaze.utils.cv_plot import plot_pose_box

from undistort import * 
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

STD_SIZE = 120

def plot(tvecs): 
    fig = plt.figure() 
    ax = fig.add_subplot(111, projection='3d') 
    # ax.scatter(tvecs[:,0], tvecs[:, 1], np.abs(tvecs[:, 2])) 
    ax.scatter(tvecs[:, 0], tvecs[:, 1], tvecs[:, 2])
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_zlim(0,5000)
    plt.show()

def get_3d_head_position(pts68, pts68_local):
    model_points = pts68_local.T 
    image_points = pts68.T[:, :2]

    camera_matrix, dist_coeffs = new_K, new_D

    (success, rvec, tvec) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs)  # SOLVEPNP_DLS

    return rvec, tvec

def plot_pose_line(image, Ps, pts68s, color=(255, 0, 0), line_width=2, length_multiplier=1):
    ''' Draw a 3D box as annotation of pose. Ref:https://github.com/yinguobing/head-pose-estimation/blob/master/pose_estimator.py
    Args:
        image: the input image
        P: (3, 4). Affine Camera Matrix.
        kpt: (2, 68) or (3, 68)
    '''
    image = image.copy()
    if not isinstance(pts68s, list):
        pts68s = [pts68s]
    if not isinstance(Ps, list):
        Ps = [Ps]
    points_2d = []
    for i in range(len(pts68s)):
        pts68 = pts68s[i]
        llength = calc_hypotenuse(pts68)
        arrow_length = llength * 7 * length_multiplier
        point_3d = []
        point_3d.append((0, 0, 0))
        point_3d.append((0, 0, arrow_length))
        point_3d = np.array(point_3d, dtype=np.float64).reshape(-1, 3)

        P = Ps[i]

        # Map to 2d image points
        point_3d_homo = np.hstack((point_3d, np.ones([point_3d.shape[0], 1])))  # n x 4
        point_2d = point_3d_homo.dot(P.T)[:, :2]

        point_2d[:, 1] = - point_2d[:, 1]
        point_2d[:, :2] = point_2d[:, :2] - np.mean(point_2d[:4, :2], 0) + np.mean(pts68[:2, :27], 1)
        point_2d = np.int32(point_2d.reshape(-1, 2))

        # Draw all the lines
        cv2.line(image, tuple(point_2d[0]), tuple(
            point_2d[1]), color, line_width, cv2.LINE_AA)
        
        points_2d.append(point_2d)

    return image, points_2d

class GazeInference(object):
    def __init__(self, device='cuda:0'):
        checkpoint_fp = 'models/gaze/phase1_wpdc_vdc.pth.tar'
        arch = 'mobilenet_1'

        self.transform = transforms.Compose([ToTensorGjz(), NormalizeGjz(mean=127.5, std=128)])

        checkpoint = torch.load(checkpoint_fp, map_location=lambda storage, loc: storage)[
            'state_dict'
        ]
        self.model = getattr(mobilenet_v1, arch)(
            num_classes=62
        )  # 62 = 12(pose) + 40(shape) +10(expression)

        model_dict = self.model.state_dict()
        # because the model is trained by multiple gpus, prefix module should be removed
        for k in checkpoint.keys():
            model_dict[k.replace('module.', '')] = checkpoint[k]
        self.model.load_state_dict(model_dict)
        
        cudnn.benchmark = True
        self.model = self.model.to(device)
        self.device=device
        self.model.eval()


    def run(self, frame, bboxes, frame_debug=None, gaze_debug= True, length_multiplier=1, face_cone=False, face_landmarks=False):

        pred_gaze = np.empty([bboxes.shape[0], 3])

        pts_res = []
        Ps = []
        tvecs = []
        points_2d = []
        for i, bbox in enumerate(bboxes):
            
            bbox = bbox[:4]
            roi_box = parse_roi_box_from_bbox(bbox)

            if frame_debug is not None and not face_cone and not face_landmarks:
                frame_debug = cv2.rectangle(frame_debug, (int(roi_box[0]), int(roi_box[1])), (int(roi_box[2]), int(roi_box[3])), (255, 255, 255), 5) 
            
            img = crop_img(frame, roi_box)
            img = cv2.resize(
                img, dsize=(STD_SIZE, STD_SIZE), interpolation=cv2.INTER_LINEAR
            )
            model_input = self.transform(img).unsqueeze(0)
            with torch.no_grad():
                model_input = model_input.to(self.device)
                param = self.model(model_input)
                param = param.squeeze().cpu().numpy().flatten().astype(np.float32)
            
            pts68, pts68_local = predict_68pts(param, roi_box)

            rvec, tvec = get_3d_head_position(pts68, pts68_local)
            tvecs.append(tvec)
            
            pts_res.append(pts68)
            
            P, pose = parse_pose(param)
            Ps.append(P)
            
            r = R.from_euler('xyz', [-pose[1] , -pose[0], -pose[2]], degrees=False)
            rot_matrix = r.as_matrix()

            rvec_, _ = cv2.Rodrigues(rot_matrix)
            tvec_ = np.array([0.0, 0.0, 1.0], np.float32)

            axis = np.float32([[0.0, 0.0, 1.0]])

            cam_w = roi_box[2] - roi_box[0]
            cam_h = roi_box[3] - roi_box[1]
            c_x = cam_w / 2
            c_y = cam_h / 2
            f_x = c_x / np.tan(60/2 * np.pi / 180)
            f_y = f_x
            camera_matrix = np.float32([[f_x, 0.0, c_x],
                                        [0.0, f_y, c_y],
                                        [0.0, 0.0, 1.0] ])
            
            camera_distortion = np.float32([0.0, 0.0, 0.0, 0.0, 0.0])
            
            imgpts, _ = cv2.projectPoints(axis, rvec_, tvec_, camera_matrix, camera_distortion)
            imgpts = imgpts.squeeze()

            p_start = [ int((roi_box[0] + roi_box[2]) / 2), int((roi_box[1] + roi_box[3]) / 2) ]
            p_stop  = [ int(roi_box[0] + imgpts[0]), int(roi_box[1] + imgpts[1])]

            pred_gaze[i] = np.array(pose).reshape(3)

            points_2d.append([p_start,p_stop])
        
        tvecs = np.array(tvecs).reshape(-1, 3)
        
        idx = np.where(tvecs[:,2] < 0)
        tvecs[idx] = -tvecs[idx]
        # tvecs[:, 1] = -tvecs[:, 1]
        
        # plot(tvecs)

        if frame_debug is not None and gaze_debug:
            if face_cone:
                frame_debug = plot_pose_box(frame_debug, Ps, pts_res)
            elif (face_landmarks):
                frame_debug = draw_landmarks(frame_debug, pts_res)
            else:
                frame_debug, points_2d = plot_pose_line(frame_debug, Ps, pts_res, length_multiplier=length_multiplier)
        return pred_gaze, frame_debug, points_2d, tvecs