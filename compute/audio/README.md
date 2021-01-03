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
<pre>
docker run \
--name "containername" \ <b>choose any unique name for container</b>
-e LOCAL_USER_ID=$(id -u) \
-v logDir:/tmp  \ <b> logDir= physical directory, present in the system, with user-level rwx permsission </b>
-v videoDir:/app/source \ <b> videoDir= Directory in which the video is present </b>
--rm \
tagname \ <b> tagname =name of the image</b>
--front_url /app/source/front_video  \ <b> front_video= student facing video </b>
--back_url /app/source/back_video  \<b> front_video= instructor facing video </b>
--time_duration 60  \<b>processes 60 (sec) of the video (configurable)</b>
</pre>
