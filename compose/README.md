Deploying EduSense
==================

We provide a set of `docker-compose` files to facilitate EduSense deployments.
For each of the docker-compose file, we set up default parameters which are
good enough to use off-the-shelf but if you want to change some parameters,
please refer to *Advanced Usage* subsection.

For more details on customizing our pipeline for your use case, please refer
to our docker compose files as they will serve as deployment examples as are.
Also, you can try help messages for each of the applications as follows:

```
docker run edusensecmu/video --help
docker run edusensecmu/audio --help
docker run edusensecmu/openpose --help
docker run edusensecmu/storage --help
```

## Contents

1. [Processing Video File](#processing-video-file)
2. [Running Storage Server](#running-storage-server)

## Processing Video File

[docker-compose.video.file.yml](compose/docker-compose.video.file.yml) starts
the video processing pipeline. It reads video file at ./input/video.avi and
outputs json (./output/video.(student|instructor).(frame\_number).json,
image (./output/video.(student|instructor).(frame\_number).jpg and annotated
video file (./output/video.avi).

To run the pipeline off-the-shelf:

1. Create directories (./input and ./output)
2. Place the video file you want to run EduSense inside ./input and name it
   video.avi. As a result, you will have the video file at ./input/video.avi.
3. Run the following command:
```
LOCAL_USER_ID=$(id -u) docker-compose -f docker-compose.video.file.yml up
```
4. Check ./output for results
5. Shutdown the system by
```
docker-compose -f docker-compose.video.file.yml down
```

### Advanced Usage

1. *Changing video path*: you can change mount points in `volumes` config. For
   example, if you want to use a video file in /home/Videos, you can change
   `./input:./input` part in `services.openpose./volumes` to
   `/home/Videos:./input`. You can also change the video file name. In this
   case, you should change one line of command list (`/input/video.avi`) at
   `services.openpose.command` to `/input/<your_video_file_name>.avi`.
2. *Processing Real Time*: By default, our pipeline tries to process every
   single frame in the video file. However, this can lead to excessive
   processing time if the video file is long enough. If you set
   `--process_real_time` flag to both of the service command line input, the
   pipeline will try to keep up with the real time, skipping some frames.
3. *Processing Instructor Frame*: By default, we run the pipeline for
   student view frames (front videos). To process instructor view, put a flag
   `--instructor` to command list of `video` service.

## Running Storage Server

EduSense also supports a web server that can support EduSense end applications.
[docker-compose.storage.yml](compose/docker-compose.storage.yml) starts the web
server with MongoDB as a database backend at port 5000.

To run the pipeline off-the-shelf:

1. *optional* Get SSL certificates if you want HTTPS. We use
   [let's encrypt](https://letsencrypt.org/) certificates that we can obtain
   easily using [CertBot](https://certbot.eff.org/).
2. Give the certificate paths (for fullchain & privkey) in the docker-compose
   file. If you do not want to enable HTTPS, which is highly discouraged, you
   can create an empty file and put the file path in `secrets:` sections of the
   docker-compose file.
3. Set up the access username/password. You can create separate files with
   username and password in text and give it to the corresponding sections
   under `secrets:` section of the docker-compose file. If you do not want to
   set the username and password, which is also highly discouraged, you can
   create an empty file and provide the file path to both of the fields. Then,
   you will get default username (`edusense`) and
   password(`onlyForDevelopmentDoNotUseDefaultPasswordInProduction`).
4. Finally, run the system with:
```
LOCAL_USER_ID=$(id -u) docker-compose -f docker-compose.storage.yml up
```
5. Shutdown the system by
```
docker-compose -f docker-compose.storage.yml down
```

### Advanced Usage
1. *Changing the port number*: If you want to change the default port
   number(5000), you would want to change the first part of `5000:5000` in
   `services.storage.ports` section. For example, if you want port number
   7000, you can change that line to `7000:5000`.
2. *Changing DB name*: By default, all the data is stored in `edusense`
   database in mongo DB. To change the DB name, change the value for
   `-db` at `services.storage.command`.
