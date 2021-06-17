EduSense Video
================
This is a repository for the video analysis component of Edusense.
## Getting Started
This instruction is for manually setting up video pipeline. For those who are new to Edusense, we recommend to take a look at 
automated multi-container setup provided [here](/compose/README.md) or use an automated script provided [here](/scripts).

<b>Note-:</b>  Video pipeline takes input from OpenPose pipeline via either local unix socket (demonstrated below, remember 
to use the same log directory for both openpose and video pipeline) or TCP socket

<b>Note-:</b> Manual setup is intended for debugging purposes, not for pushing analysis data to the storage backend.



#### Build image
```
docker build .
```

You may also want to name the image like below:
```
docker build . -t <tag_name>
```
#### Running Container
Make a log directory (log_dir) and pass the path to the docker run command. Make sure, to have a video in a video directory,pass the directory path and the video name to the docker run command.
```
docker run \
--name <unique name for container> \
-e LOCAL_USER_ID=$(id -u) \       
-e CUDA_VISIBLE_DEVICES=-1 \
-v <log_dir: path of the log dir>:/tmp \
-v <video_dir: path of the video directory>:/app/source \
<image name for the container/tag_name with which the image is built>\
--video_sock /tmp/unix.front.sock  \
--use_unix_socket \
--keep_frame_number \
--process_gaze \
--profile \
--time_duration <timeout: processing time duration>  \
--process_real_time  \
--video /app/source/<videoname = name of the video> \
```
<b>Note-: Make sure you log directory has 777 permissions, or else you will see following errors:
```bash
Error:
failed to establish connection to unix socket

Coming from:
- /openpose/examples/edusense/edusense.cpp:initializationOnThread():261
- /openpose/include/openpose/thread/worker.hpp:initializationOnThreadNoException():77
- /openpose/include/openpose/thread/subThread.hpp:initializationOnThread():150
- /openpose/include/openpose/thread/thread.hpp:initializationOnThread():173
- /openpose/include/openpose/thread/thread.hpp:threadFunction():203
- /openpose/include/openpose/thread/thread.hpp:exec():128
- /openpose/include/openpose/thread/threadManager.hpp:exec():202
- /openpose/include/openpose/wrapper/wrapper.hpp:exec():424
terminate called after throwing an instance of 'boost::exception_detail::clone_impl<boost::exception_detail::error_info_injector<boost::system::system_error> >'
  what():  write: Transport endpoint is not connected
```
<b>Note-:</b> For real-time processing, pass the RTSP URL to video argument.

<b>Note-:</b> The above command represents a rather small section of the configurable arguments, 
all the configurable flags can be found [here](/compute/video/python/video_pipeline.py)
