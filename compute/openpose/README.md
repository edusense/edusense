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
Make a log directory (log_dir) and pass the path to the docker run command. Make sure, to have a video in a video directory,pass the directory path and the video name to the docker run command.
```
nvidia-docker run \
--name <unique name for container> \
--rm \
-e LOCAL_USER_ID=$(id -u) \
-v <log_dir: path of the log dir>:/tmp \
-v <video_dir: path of the video directory>:/app/video \
<image name for the container/tag_name with which the image is built>\
--video /app/video/<videoname = name of the video> \
--num_gpu_start <GPU number to be assigned to the container>  \
--num_gpu <Number of GPU assigned to the container(preferred 1)> \ 
--use_unix_socket \
--unix_socket /tmp/unix.front.sock \
--display 0 \
--render_pose 0 \
--raw_image \
--process_real_time \
```
<b>Note-:</b> For real-time processing, pass the RTSP URL to ip_camera argument

<b>Note-: Openpose Fail on Nvidia 2080Ti(and later) GPUs:</b> Openpose runtime 
will not work with Nvidia 2080 Ti GPUs, because linked cafee codebase does not 
support newer GPU architecture.

For correcting this, you 
need to manually change cmake file for caffe. Follow the instructions below 
(copied from [https://github.com/CMU-Perceptual-Computing-Lab/openpose/issues/1290#issuecomment-546578933]())
```bash
# Add GPU architectures directly to Cuda.cmake file for caffe
cd {Edusense_ROOT}/compute/openpose/third_party/openpose/3rdparty/
git clone https://github.com/CMU-Perceptual-Computing-Lab/caffe
then,
open Cuda.cmake file in cmake folder.
then directly added information like this,

Known NVIDIA GPU achitectures Caffe can be compiled for.
This list will be used for CUDA_ARCH_NAME = All option
# adding 70 and 75 in this line
set(Caffe_known_gpu_archs "30 35 50 52 60 61 70 75")
...

if(${CUDA_ARCH_NAME} STREQUAL "Fermi")
set(__cuda_arch_bin "20 21(20)")
elseif(${CUDA_ARCH_NAME} STREQUAL "Kepler")
set(__cuda_arch_bin "30 35")
elseif(${CUDA_ARCH_NAME} STREQUAL "Maxwell")
set(__cuda_arch_bin "50")
elseif(${CUDA_ARCH_NAME} STREQUAL "Pascal")
set(__cuda_arch_bin "60 61")
#add following config for 70 and 71
#<<<
elseif(${CUDA_ARCH_NAME} STREQUAL "Volta")
set(__cuda_arch_bin "70")
elseif(${CUDA_ARCH_NAME} STREQUAL "Turing")
set(__cuda_arch_bin "75")
#>>>
elseif(${CUDA_ARCH_NAME} STREQUAL "All")
set(__cuda_arch_bin ${Caffe_known_gpu_archs})
elseif(${CUDA_ARCH_NAME} STREQUAL "Auto")
caffe_detect_installed_gpus(__cuda_arch_bin)
else() # (${CUDA_ARCH_NAME} STREQUAL "Manual")
set(__cuda_arch_bin ${CUDA_ARCH_BIN})
endif()

# Remove and Rebuild docker image
```
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
