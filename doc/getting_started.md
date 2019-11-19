Getting Started with EduSense
=============================

## Contents

1. [Requirements](#requirements)
    1. [Operating Systems](#operating-systems)
2. [Installing Dependencies](#installing-dependencies)
3. [Buildling/Deploying EduSense](#buildingdeploying-edusense)
    1. [EduSense Components](#edusense-components)
    2. [Deploying EduSense (Production)](#deploying-edusense-production)
    3. [Deploying EduSense (Development)](#deploying-edusense-development)

## Requirements

### Operating Systems

We packaged all components of our system into [Docker](https://www.docker.com)
containers. EduSense should be deployable on any Linux distributions with
proper docker daemon installed. Currently, we do not support Windows/Mac
deployments.

## Installing Dependencies

1. Install **nvidia-docker**: [nvidia-docker2 installation doc](https://github.com/NVIDIA/nvidia-docker/wiki/Installation-(version-2.0)).
    * When you are done installing Docker, please make sure you also follow post-installation [steps](https://docs.docker.com/install/linux/linux-postinstall)
    * Note: With Docker >= 19.03, GPUs are natively supported by Docker daemon,
      but `docker-compose` does not support GPU allocation as of now. We stick
      to to-be-deprecated nvidia-docker for current deployment. Once the new
      version of docker-compose gets released, we will explore ways to use the
      new functionality.
2. Install **docker-compose**: [docker-compose installation doc](https://docs.docker.com/compose/install/)

## Building/Deploying EduSense

### EduSense Components

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

We provide a set of [docker compose files](compose/) that automates compilation
and deploys EduSense. For more details on each of the docker-compose files,
please refer to [readme file](compose/README.md).

We are glad to see you interested in developing with us! We always welcome
new contributors. Please feel free to discuss what you found or what you want
to do in our issue page.
