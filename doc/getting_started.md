Getting Started with EduSense
=============================

## Contents

1. [Requirements](#requirements)
    1. [Operating Systems](#operating-systems)
    2. [Dependencies](#dependencies)
3. [EduSense Component Overview](#edusense-component-overview)
4. [Deploying EduSense](#deploying-edusense)
5. [Using EduSense APIs for Client Development](#using-edusense-apis-for-client-development)

## Requirements

### Operating Systems

We packaged all components of our system into [Docker](https://www.docker.com)
containers. EduSense should be deployable on any Linux distributions with
proper docker daemon installed. Currently, we do not support Windows/Mac
deployments.

### Dependencies

1. Download **cuda** : [cuda installation](https://developer.nvidia.com/cuda-downloads). Reboot the machine, after installing cuda

2. Check the driver : 
```
lspci -nnk
```
Output should contain:
<pre>
00:05.0 VGA compatible controller [0300]: NVIDIA Corporation GP102 [GeForce GTX 1080 Ti] [10de:1b06] (rev a1)
    Subsystem: eVga.com. Corp. GP102 [GeForce GTX 1080 Ti] [3842:5390]
    Kernel driver in use: <b>nvidia</b>
    Kernel modules: nvidiafb, nouveau, nvidia_drm, nvidia
00:06.0 Audio device [0403]: NVIDIA Corporation GP102 HDMI Audio Controller [10de:10ef] (rev a1)
    Subsystem: eVga.com. Corp. GP102 HDMI Audio Controller [3842:5390]
    Kernel driver in use: snd_hda_intel
    Kernel modules: snd_hda_intel
</pre>
3.  **Optional** If nouveau driver grabs GPUs in step 2, follow the instructions for blacklisting nouveau.

Open /etc/modprobe.d/blacklist-nvidia-nouveau.conf and add
```
blacklist nouveau
options nouveau modeset=0
```
Then run
```
sudo update-initramfs -u
```
Reboot the machine and confirm the driver in use-:
```
lspci -nnk | grep "NVIDIA"
```
The output should look like:
<pre>
00:05.0 VGA compatible controller [0300]: NVIDIA Corporation GP102 [GeForce GTX 1080 Ti] [10de:1b06] (rev a1)
    Subsystem: eVga.com. Corp. GP102 [GeForce GTX 1080 Ti] [3842:5390]
    Kernel driver in use: <b>nvidia</b>
    Kernel modules: nvidiafb, nouveau
00:06.0 Audio device [0403]: NVIDIA Corporation GP102 HDMI Audio Controller [10de:10ef] (rev a1)
    Subsystem: eVga.com. Corp. GP102 HDMI Audio Controller [3842:5390]
    Kernel driver in use: snd_hda_intel
    Kernel modules: snd_hda_intel
</pre>

4. Install **nvidia-docker**: [nvidia-docker installation doc](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker).
    * When you are done installing Docker, please make sure you also follow post-installation [steps](https://docs.docker.com/install/linux/linux-postinstall)
    * Note: With Docker >= 19.03, GPUs are natively supported by Docker daemon,
      but `docker-compose` does not support GPU allocation as of now. We stick
      to to-be-deprecated nvidia-docker for current deployment. Once the new
      version of docker-compose gets released, we will explore ways to use the
      new functionality.
     
5. Run-:
```
docker run --runtime=nvidia --rm nvidia/cuda nvidia-smi
```

6. Install **docker-compose**: [docker-compose installation doc](https://docs.docker.com/compose/install/)

## EduSense Component Overview

EduSense is composed of multiple components packaged as separate Docker
components.

* Compute Pipeline
  * **openpose** runs native openpose application with additional minimal API
    that feeds the output to video pipeline. This part is referred as *Scene
    Parsing* in the paper.
  * **video** post-processes and featurizes the openpose output. This component
    is noted as *Video Featurization Modules* in the paper. This module can
    write the output to JSON / JPG / video files or send it out to our storage
    backend.
  * **audio** processes audio data end-to-end. This module can send the output
    to our storage backend. This component is referred as *Audio Featurization
    Modules* in the paper.
* Storage Backend
  * **storage** supports REST API end points for the compute pipelines
    mentioned above and EduSense client applications. Our storage backend
    depends on MongoDB as database backend.
* Frontend (not included in this repository)
  * **frontend** visualizes processed data, providing useful debug interface.
    Currently, our edusense repository does not contain this component.
    
## Deploying EduSense

To faciliate deployment, we packaged each component of EduSense into Docker
containers. We provide Dockerfiles for each components and docker-compose files
that automates multi-container deployment. 

We provide a set of [docker compose files](/compose/) that automates compilation
and deploys EduSense. Feel free to take a look at the directory for more information.

## Using EduSense APIs for Client Development

Storage server supports a set of HTTP RESTful APIs for custom EduSense applications
(App Layer in the paper). Please refer to this [documentation](/doc/developer_guide.md)
for more details about the client API.

## Contributing to EduSense

We are glad to see you interested in developing with us! We always welcome
new contributors. Please feel free to discuss what you found or what you want
to do in our issue page.
