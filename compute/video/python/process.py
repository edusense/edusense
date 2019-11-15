# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.

import math
import os

import cv2
import numpy as np
from scipy.spatial import distance as dist
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib

model_dir = os.getenv('MODEL_DIR', './models')
clf_sit_stand = joblib.load(os.path.join(model_dir, 'stand_svc.pkl'))
clf_posture = joblib.load(os.path.join(model_dir, 'posture.pkl'))
clf_smile = joblib.load(os.path.join(model_dir, 'smile_svc.pkl'))
clf_mouth = joblib.load(os.path.join(model_dir, 'mouth_svc.pkl'))

def unit_vector(vector):
    if np.linalg.norm(vector) == 0:
        return vector
    return vector / np.linalg.norm(vector)

def get_unit_vec_mouth(x,y):
    feature = []
    for i in range(0,len(x)):
        if (x[i] == 0 or y[i] == 0):
            return -1
    for i in range(1,len(x)):
        vec = (x[i]-x[0],y[i]-y[0])
        vec_u = unit_vector(vec)
        feature.append(vec_u[0])
        feature.append(vec_u[1])
    return feature

def predict_mouth_open(x,y,c):
    mouth = ""
    fv = 0
    for k in range(0,len(x)):
        if (x[k] == 0 or y[k] == 0):
            fv = -1
            color = (0,0,255)
            return "error", color
    if fv != -1:
        p1 = [x[0],y[0]]
        p2 = [x[6],y[6]]
        p3 = [x[3],y[3]]
        p4 = [x[9],y[9]]
        A = dist.euclidean(p1, p2)
        B = dist.euclidean(p3, p4)
        d1 = A
        d2 = B
        if A == 0:
            e1 = 0
        else:
            e1 = B/float(A)
        p1 = [x[12],y[12]]
        p2 = [x[16],y[16]]
        p3 = [x[14],y[14]]
        p4 = [x[18],y[18]]
        A = dist.euclidean(p1, p2)
        B = dist.euclidean(p3, p4)
        d3 = A
        d4 = B
        if A == 0:
            e2 = 0
        else:
            e2 = B/float(A)
        fv = [e1,e2]
        fv = np.array(fv)
        fv = fv.reshape(1,-1)
        out = clf_mouth.predict(fv)
        if out == 1:
            mouth = "open"
            color = (0,255,127)
        else:
            mouth = "close"
            color = (0,255,255)
    return mouth, color

def predict_mouth(face_points):
    x_face = face_points[0::3]
    y_face = face_points[1::3]
    c_face = face_points[2::3]
    x_face = x_face[48:68]
    y_face = y_face[48:68]
    c_face = c_face[48:68]
    out_mouth, mouth_color = predict_mouth_open(x_face,y_face,c_face)
    fv = get_unit_vec_mouth(x_face,y_face)
    if fv == -1:
        out_smile = "error"
        out_mouth = "error"
        color = (0,0,255)
        mouth_color = (0,0,255)
    else:
        fv = np.array(fv)
        fv = fv.reshape(1,-1)
        out = clf_smile.predict(fv)
        if out == 1:
            out_smile = "smile"
            color = (0,255,0)
        else:
            out_smile = "noSmile"
            color = (0,127,255)
    for i in [12,16,14,18,0,3,6,9]:
        if c_face[i] < 0.5:
            out_smile = "error"
            out_mouth = "error"
            color = (0,0,255)
            mouth_color = (0,0,255)
    return out_mouth, mouth_color, out_smile, color

def get_unit_vec_armpose(x,y):
    feature = []
    for i in range(0,len(x)):
        if (x[i] == 0 or y[i] == 0):
            return -1
    shoulder_width = dist.euclidean([x[2],y[2]],[x[5],y[5]])
    neck_height = dist.euclidean([x[0],y[0]],[x[1],y[1]])

    for i in range(0,len(x)):
        for j in range(i,len(x)):
            vec = (x[i]-x[j],y[i]-y[j])
            p1 = [x[i],y[i]]
            p2 = [x[j],y[j]]
            if neck_height == 0:
                return -1
            A = dist.euclidean(p1, p2)/float(neck_height)
            feature.append(A)
            vec = unit_vector(vec)
            feature.append(vec[0])
            feature.append(vec[1])
    return feature

def predict_armpose(body_points):
    poses = []
    out_posture = ""
    x = body_points[0::3]
    y = body_points[1::3]
    c = body_points[2::3]
    key_pts = []
    for i in range(len(x)):
        key_pts.append([x[i],y[i],c[i]])
    poses.append(key_pts)
    x_new = []
    y_new = []
    c_new = []
    for j in [0,1,2,3,4,5,6,7]:
        x_new.append(x[j])
        y_new.append(y[j])
        c_new.append(c[j])
    fv = get_unit_vec_armpose(x_new,y_new)
    out_posture = ""
    color = (0,0,255)
    if (y_new[4]<y_new[3] and y_new[3] < y_new[2] and y_new[2]!=0 and y_new[3]!=0 and y_new[4]!=0) or (y_new[7] < y_new[6] and y_new[6] < y_new[5] and y_new[5]!=0 and y_new[6]!=0 and y_new[7]!=0):
        out_posture = 'handsRaised'
        color = (0,255,0)
    elif fv == -1:
        out_posture = 'error'
        color = (0,0,255)
    else:
        fv = np.array(fv)
        fv = fv.reshape(1,-1)
        out = clf_posture.predict(fv)

        out_posture = out[0]
        if out_posture == 'hands_raised':
            out_posture = 'other'
            color = (255,0,255)
        elif out_posture == 'arms_crossed':
            out_posture = 'armsCrossed'
            color = (0,255,255)
        elif out_posture == 'hands_on_face':
            out_posture = 'handsOnFace'
            color = (255,255,255)
        else:
            color = (255,0,255)
    return out_posture, color, key_pts

# Sit stand
# ---------
def get_unit_vec_sit_stand(x,y,c):
    feature = []
    for i in range(0,len(x)):
        if (x[i] == 0 or y[i] == 0):
            return -1
    for i in range(1,len(x)):
        for j in range(i+1,len(x)):
            vec = (x[j]-x[i],y[j]-y[i])
            vec_u = unit_vector(vec)
            feature.append(vec_u[0])
            feature.append(vec_u[1])
    top_point = [x[0],y[0]]
    left_point = [x[2],y[2]]
    right_point = [x[5],y[5]]
    down_point_left = [x[3],y[3]]
    down_point_right = [x[6],y[6]]
    v_dist1 = dist.euclidean(top_point, down_point_left)/dist.euclidean(top_point, left_point)
    v_dist2 = dist.euclidean(top_point, down_point_right)/dist.euclidean(top_point, right_point)
    return feature + [v_dist1,v_dist2]

def predict_sit_stand(body_points):
    poses = []
    out_stand = ""
    x = body_points[0::3]
    y = body_points[1::3]
    c = body_points[2::3]
    key_pts = []
    for i in range(len(x)):
        key_pts.append([x[i],y[i],c[i]])
    poses.append(key_pts)
    x_new = []
    y_new = []
    c_new = []
    for j in [1,9,10,11,12,13,14]:
        x_new.append(x[j])
        y_new.append(y[j])
        c_new.append(c[j])
    fv = get_unit_vec_sit_stand(x_new,y_new,c_new)
    if fv == -1:
        out_stand = "error"
        color = (0,0,255)
    else:
        fv = np.array(fv)
        fv = fv.reshape(1,-1)
        out = clf_sit_stand.predict(fv)
        out = out[0]
        if out == 'stand':
            out_stand = "stand"
            color = (0,255,127)
        else:
            out_stand = "sit"
            color = (0,255,255)
    return out_stand, color, key_pts


def get_pose_pts(body_keypoints):
    pose = []
    for i in range(int(len(body_keypoints)/3)):
        pose.append((int(body_keypoints[3*i]), int(body_keypoints[3*i+1]), int(body_keypoints[3*i+2])))
    return pose

def check_body_pts(body_keypoints):
    valid_pts = 0
    for i in range(int(len(body_keypoints)/3)):
        if body_keypoints[3*i+2] > 0.3 and body_keypoints[3*i] > 0 and body_keypoints[3*i+1] > 0:
            valid_pts += 1
    return (valid_pts > 7)

def prune_body_pts(body_keypoints):
    distance_thresh = 800
    for i in range(int(len(body_keypoints)/3)):
        if body_keypoints[3*i+2] < 0.25:
            body_keypoints[3*i+2] = 0
            body_keypoints[3*i+1] = 0
            body_keypoints[3*i] = 0
        else:
            body_keypoints[3*i+2] = 1
    line_draw = [[1,2,3,4],[1,5,6,7],[1,8,9,10,11],[1,8,12,13,14],[1,0,16,18],[0,15,17]]
    for limbs in line_draw:
        for i in range(0,len(limbs)-1):
            x1 = body_keypoints[3*limbs[i]]
            y1 = body_keypoints[3*limbs[i] + 1]
            x2 = body_keypoints[3*limbs[i+1]]
            y2 = body_keypoints[3*limbs[i+1] + 1]
            if x1!=0 and x2!=0 and y1!=0 and y2!=0:
                limb_length = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                if limb_length > distance_thresh:
                    body_keypoints[3*limbs[i]] = 0
                    body_keypoints[3*limbs[i] + 1] = 0
                    body_keypoints[3*limbs[i] + 2] = 0
                    body_keypoints[3*limbs[i+1]] = 0
                    body_keypoints[3*limbs[i+1] + 1] = 0
                    body_keypoints[3*limbs[i+1] + 2] = 0
    return body_keypoints

def get_face(pose):
    x1 = pose[0][0]
    y1 = pose[0][1]
    x2 = pose[1][0]
    y2 = pose[1][1]
    if x1 == 0 or x2 == 0 or y1 ==0 or y2 == 0:
        return None

    p1 = (int(x1-32),int(y1-32))
    p2 = (int(x1+32),int(y1+32))

    return (p1,p2)

def get_pose_box(pose):
    return np.array([int(pose[1][0])-1,int(pose[1][1])-1,int(pose[1][0])+1,int(pose[1][1])+1])

def get_3d_head_position(pose,size):
    image_points = np.array([
                            (pose[0][0], pose[0][1]),     # Nose tip
                            (pose[15][0], pose[15][1]),   # Right eye
                            (pose[14][0], pose[14][1]),   # Left eye
                            (pose[17][0], pose[17][1]),   # Right ear
                            (pose[16][0], pose[16][1]),   # Left ear
                        ], dtype="double")
    model_points = np.array([
                            (-48.0, 0.0, 21.0),       # Nose tip
                            (-5.0, -65.5, -20.0),     # Right eye 
                            (-5.0, 65.6, -20.0),      # Left eye
                            (-6.0, -77.5, -100.0),    # Right ear
                            (-6.0, 77.5, -100.0)      # Left ear 
                         ])

    c_x = size[1]/2
    c_y = size[0]/2
    f_x = c_x / np.tan(60/2 * np.pi / 180 )
    f_y = f_x

    camera_matrix = np.array(
                         [[f_x, 0, c_x],
                         [0, f_y, c_y],
                         [0, 0, 1]], dtype = "double"
                         )
    dist_coeffs = np.zeros((4,1))
    (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
    tvec = (int(translation_vector[0]/100.0),int(translation_vector[1]/100.0),abs(int(translation_vector[2]/100.0))) 
    return tvec

def get_pose_pts(body_keypoints):
    pose = []
    for i in range(int(len(body_keypoints)/3)):
        pose.append((int(body_keypoints[3*i]), int(body_keypoints[3*i+1]), int(body_keypoints[3*i+2])))
    return pose


def get_facing_direction(pose):
    facing_direction = "error"

    if pose[5][0] != 0 or pose[2][0] != 0:
        if pose[5][0] > pose[2][0]:
            facing_direction = "front"
        else:
            facing_direction = "back"

    return facing_direction
