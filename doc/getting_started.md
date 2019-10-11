Getting Started with EduSense
=============================

## Contents

1. [Requirements](#requirements)
  1. [Operating Systems](#operating-systems)
  1. [Installing Dependencies](#installing-dependencies)
  1. [Buildling/Deploying EduSense](#building/deploying-edusense)
    1. [EduSense Components](#edusense-components)
    1. [Deploying EduSense (Production)](#deploying-edusense-(production))
    1. [Deploying EduSense (Development)](#deploying-edusense-(development))

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
    but `docker-compose` does not support GPU allocation as of now. We stick to
    soon-to-be-deprecated nvidia-docker for current deployment. Once the new
    version of docker-compose gets released, we will explore ways to use the
    new functionality.
1. Install **docker-compose**: [docker-compose installation doc](https://docs.docker.com/compose/install/)

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

We have two options for deployment: deploying EduSense for development and
for production. **If you make any changes to the code base and want to test
your component, please use the instructions for
[deploying EduSense for development](#deploying-edusense-(development)). If you
just want to deploy EduSense in production, please the instructions in
[deploying EduSense for production](#deploying-edusense-(production))**

### Deploying EduSense (Production)

We have all our container images available at [docker hub](https://hub.docker.com/u/edusensecmu).
As our system has multiple components to be deployed, we provide at set of
docker compose files that automatically download the images from the hub and
set up the connections among the containers. For more details, please refer to
[EduSense production repository](https://www.github.com/edusense/production).

### Deploying EduSense (Development)

We are glad to see you interested in developing with us! We always welcome
new contributors. Please feel free to discuss what you found or what you want
to do in our issue page.

We provide a set of [docker compose files](compose/) that automates compilation
and deploys EduSense. For more details on each of the docker-compose files,
please refer to [readme file](compose/README.md).

