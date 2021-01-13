# Reference:
# https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-333b05afa0b0

import numpy as np 
import sys 
import cv2

DIM = (3840, 2160)
K = np.array([  [2024.9176274155336, 0.0, 1869.9892811717527], 
                [0.0, 1995.8166344455785, 1074.7218398706427], 
                [0.0, 0.0, 1.0]])
D = np.array([  [-0.018902597165528764], [0.01548068392534243], 
                [-0.03631135875142938], [0.0227629440543949]])

balance=1.0
dim2=None
dim3=None

dim1 = DIM  #dim1 is the dimension of input image to un-distort
assert dim1[0]/dim1[1] == DIM[0]/DIM[1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"
if not dim2:
    dim2 = dim1
if not dim3:
    dim3 = dim1
scaled_K = K * dim1[0] / DIM[0]  # The values of K is to scale with image dimension.
scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0
# This is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, 
                D, dim2, np.eye(3), balance=balance)
map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), 
                new_K, dim3, cv2.CV_16SC2)

new_D = np.zeros((4, 1))
# print("f = np.array(" + str(new_K.diagonal()[:2].tolist()) + ")")
# print("c = np.array(" + str(new_K[:2, 2].tolist()) + ")")

def undistort(img):
    undistorted_img = cv2.remap(img, map1, map2, 
                    interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    
    return undistorted_img
