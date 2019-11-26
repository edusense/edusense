EduSense Compute
================

EduSense Compute has three compute backend modules: openpose, video featurization and audio featurization modules.

## Developer Guide

### Directory Structure

* **[audio](audio)**: Audio pipeline
* **[video](video)**: Video pipeline
* **[openpose](openpose)**: OpenPose pipeline

### How to compose each module

#### Audio Pipeline

Audio pipeline is a stand-alone component that does not depend on other compute modules.
It takes two video files or rtsp streams as input and post the audio frames to our
EduSense storage backend.

#### OpenPose Pipeline

OpenPose pipeline takes one video file or rtsp stream as input and extracts body/face
keypoints. The keypoint results are sent to video pipeline via either local unix socket
or TCP socket. For OpenPose to start posting the keypoint results to video pipeline, the
video pipeline should be ready and have the sockets listening for new connections.

#### Video Pipeline

Video pipeline extracts all the other features from the keypoints and the video frame.
Video pipeline takes input from OpenPose pipeline via either local unix socket or TCP socket.
To take inputs, video pipeline should first start a socket server and listen for new
connections from openpose pipeline. Currently, only one OpenPose pipeline can post to
one video pipeline.
