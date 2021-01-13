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

def get_3d_pose(frame, face_points):

    # # Get faces
    # faces, _ = retinaface.run(frame, frame_debug=None)
    
    # if faces.shape[0] == 0:
    #     print("Faces not found in the image.")
    #     return [None, None, None], [None, None, None]

    # Get Gaze
    pred_gazes, _, _, tvecs = gaze.run(frame, face_points, frame_debug=None)

    if not pred_gazes.shape[0] == 1:
        print("No or more than one face found in the image.")
        return [None, None, None], [None, None, None]

    return tvecs[0], pred_gazes[0]
