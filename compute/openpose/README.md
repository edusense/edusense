EduSense Openpose
=================
This is a repository for the openpose component of Edusense.
## Getting Started
This instruction is for manually setting up openpose pipeline. For those who are new to Edusense, we recommend to take a look at 
automated multi-container setup provided [here](/compose/README.md) or use an automated script provided [here](/scripts).

<b>Note-:</b>  Openpose pipeline processes the video, extracts the keypoints and sends them to the video pipeline via either local unix socket (demonstrated below, remember to use the same log directory for both openpose and video pipeline) or TCP socket

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
nvidia-docker run \
--name  "containername" \ <b>choose any unique name for container</b>
--rm \
-e LOCAL_USER_ID=$(id -u) \
-v logDir:/tmp  \ <b> logDir= physical directory, present in the system, with user-level rwx permsission </b>
-v videoDir:/app/video \ <b> videoDir= Directory in which the video is present </b>
tagname \ <b> tagname= name of the image</b>
--video video_name \ <b> video_name= name of the video </b>
--num_gpu_start 0  \
--num_gpu 1 \   <b>assign 1 GPU starting from num_gpu_start</b>
--use_unix_socket \
--unix_socket /tmp/unix.front.sock \
--display 0 \
--render_pose 0 \
--raw_image \
--process_real_time \
</pre>
## Developer Guide

### Keeping up with OpenPose Releases

When compiling, we inject our EduSense code into OpenPose code base. OpenPose is
a library under active development; our code often fails to compile because of
code changes (e.g., API and data structure) in newer versions of OpenPose. We need
to update our code whenever we integrate newer OpenPose into EduSense.

We release our EduSense code as patch diff files. The original source code we derive
the current patch files from is /openpose/examples/tutorial_api_cpp/16_synchronous_custom_output.cpp .
The file names of the code changes time to time, so we need to track file changes
across OpenPose versions.

To generate a diff patch file,

```
diff <original file> <new edusense file> > edusense/edusense.cpp.patch
```

Once the patch file is ready, we also need to modify Dockerfile to update the path
to the original source file. A new patch file lacks license notices, so
we need to update the patch file also.

To apply a patch to a file:

```
patch <original file> -i examples/edusense/edusense.cpp.patch -o examples/edusense/edusense.cpp
```

If a developer also wants to update CMakefile, he/she can follow the same instructions
noted above.
