EduSense Audio
================
This is a repository for the audio analysis component of Edusense.
## Getting Started
This instruction is for manually setting up audio pipeline. For those who are new to Edusense, we recommend to use an automated 
script provided [here](/scripts). 

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
Make a log directory (log_dir) and pass the path to the docker run command. Make sure, to have a front(student facing) and back(instructor facing) video in the same video directory, pass the directory path and the video names to the docker run command.
```
docker run \
--name <unique name for container> \
-e LOCAL_USER_ID=$(id -u) \
-v <log_dir: path of the log dir>:/tmp  \
-v <video_dir: path of the video directory>:/app/source \
--rm \
<image name for the container/tag_name with which the image is built>\
--front_url /app/source/<student facing video>  \
--back_url /app/source/<instructor facing video>  \
--time_duration <timeout: processing time duration>  \
```
<b>Note-:</b> For real-time processing, pass the RTSP URL to the front_url and back_url arguments 
