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
<pre>
docker run \
--name "containername" \ <b>choose any unique name for container</b>
-e LOCAL_USER_ID=$(id -u) \       
-e CUDA_VISIBLE_DEVICES=-1 \
-v logDir:/tmp  \ <b> logDir= physical directory, present in the system, with user-level rwx permsission </b>
-v videoDir:/app/source \ <b> videoDir= Directory in which the video is present </b>
--rm \            
tagname \ <b> tagname= name of the image</b>
--video_sock /tmp/unix.front.sock  \
--use_unix_socket \
--keep_frame_number \
--process_gaze \
--profile \
--time_duration 60 \ <b> processes 60 (sec) of the video (configurable) </b>
--process_real_time  \
--video /app/source/videoName  \ <b> videoName= name of the video, present in the directory</b>

</pre>

<b>Note-:</b> The above command represents a rather small section of the configurable arguments, 
all the configurable flags can be found [here](/compute/video/python/video_pipeline.py)
