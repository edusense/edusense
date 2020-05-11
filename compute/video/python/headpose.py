#!/usr/bin/env python

# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.
# EduSense Note: Code modified from deepgaze/examples/ex_cnn_head_pose_axes/ex_cnn_head_pose_estimation_axes.py (oct 2019).
# Original license is also included below:

# The MIT License (MIT)
# Copyright (c) 2016 Massimiliano Patacchiola
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# In this example the Deepgaze CNN head pose estimator is used to get the YAW angle.
# The angle is projected on the input images and showed on-screen as a red line.
# The images are then saved in the same folder of the script.

import numpy as np
import os
import tensorflow as tf
import cv2
from deepgaze.head_pose_estimation import CnnHeadPoseEstimator
from scipy.spatial.transform import Rotation as R

is_cuda_set = os.getenv('CUDA_VISIBLE_DEVICES')
if is_cuda_set is None:
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

has_gpu = False
if tf.test.gpu_device_name():
    print('GPU found')
    has_gpu = True
else:
    print("No GPU found")

config = tf.ConfigProto(allow_soft_placement=True)
if has_gpu:
    config.gpu_options.per_process_gpu_memory_fraction = 0.5
sess = tf.Session(config=config) #Launch the graph in a session.
my_head_pose_estimator = CnnHeadPoseEstimator(sess) #Head pose estimation object

model_dir = os.getenv('MODEL_DIR', './models')
# Load the weights from the configuration folders
my_head_pose_estimator.load_yaw_variables(os.path.join(model_dir, 'headpose', 'yaw', 'cnn_cccdd_30k.tf'))
my_head_pose_estimator.load_roll_variables(os.path.join(model_dir, 'headpose', 'roll', 'cnn_cccdd_30k.tf'))
my_head_pose_estimator.load_pitch_variables(os.path.join(model_dir, 'headpose', 'pitch', 'cnn_cccdd_30k.tf'))

def get_head_pose_vector(image, face):
    cam_w = image.shape[1]
    cam_h = image.shape[0]
    c_x = cam_w / 2
    c_y = cam_h / 2
    f_x = c_x / np.tan(60/2 * np.pi / 180)
    f_y = f_x
    camera_matrix = np.float32([[f_x, 0.0, c_x],
                                [0.0, f_y, c_y],
                                [0.0, 0.0, 1.0] ])
    # print("Estimated camera matrix: \n" + str(camera_matrix) + "\n")
    #Distortion coefficients
    camera_distortion = np.float32([0.0, 0.0, 0.0, 0.0, 0.0])
    #Defining the axes
    axis = np.float32([[0.0, 0.0, 0.0],
                       [0.0, 0.0, 0.0],
                       [0.0, 0.0, 0.5]])

    roll_degree = my_head_pose_estimator.return_roll(image, radians=False)  # Evaluate the roll angle using a CNN
    pitch_degree = my_head_pose_estimator.return_pitch(image, radians=False)  # Evaluate the pitch angle using a CNN
    yaw_degree = my_head_pose_estimator.return_yaw(image, radians=False)  # Evaluate the yaw angle using a CNN
    # print("Estimated [roll, pitch, yaw] (degrees) ..... [" + str(roll_degree[0,0,0]) + "," + str(pitch_degree[0,0,0]) + "," + str(yaw_degree[0,0,0])  + "]")
    #Getting rotation and translation vector
    #Deepgaze use different convention for the Yaw, we have to use the minus sign
    #Attention: OpenCV uses a right-handed coordinates system:
    #Looking along optical axis of the camera, X goes right, Y goes downward and Z goes forward.
    pitch_degree = pitch_degree.squeeze()
    yaw_degree = yaw_degree.squeeze()
    roll_degree = roll_degree.squeeze()

    r = R.from_euler('xyz', [pitch_degree, -yaw_degree, roll_degree], degrees=True)
    rot_matrix = r.as_dcm()

    rvec, jacobian = cv2.Rodrigues(rot_matrix)
    tvec = np.array([0.0, 0.0, 1.0], np.float) # translation vector

    imgpts, jac = cv2.projectPoints(axis, rvec, tvec, camera_matrix, camera_distortion)
    p_start = (face[0][0] + int(c_x), face[0][1] + int(c_y))
    p_stop = (face[0][0] + int(imgpts[2][0][0]), face[0][1] + int(imgpts[2][0][1]))

    return yaw_degree, pitch_degree, roll_degree, p_start, p_stop
