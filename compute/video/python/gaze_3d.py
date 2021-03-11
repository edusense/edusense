import sys
import cv2
import json
import math 
import os, glob

from FaceWrapper import RetinaFaceInference
from GazeWrapper import GazeInference
from undistort import * 

retinaface = RetinaFaceInference()
gaze = GazeInference()

def get_3d_pose(frame, face_points,original_face):

    frame_temp = frame.copy()
    frame_temp = frame_temp[face_points[0][1]:face_points[0][3], face_points[0][0]:face_points[0][2]]

    # Get faces
    faces, _ = retinaface.run(frame_temp, frame_debug=None)
    

    if faces.shape[0] == 0:
        print("Faces not found in the image.")
        return np.array([None, None, None]), np.array([None, None, None]), np.array([[None, None], [None, None]]),original_face
    
    faces[0][0] += face_points[0][0]
    faces[0][1] += face_points[0][1]
    faces[0][2] += face_points[0][0]
    faces[0][3] += face_points[0][1]
    
    # Get Gaze
    pred_gazes, _, points_2d, tvecs = gaze.run(frame, face_points, frame_debug=None)

    if not pred_gazes.shape[0] == 1:
        print("No or more than one face found in the image.")
        return np.array([None, None, None]), np.array([None, None, None]), np.array([[None, None], [None, None]]),original_face

    faces = faces[0][:4]
    faces = ((int(faces[0]),(int(faces[1]))),(int(faces[2]),(int(faces[3]))))
    return tvecs[0], pred_gazes[0], points_2d[0],faces
