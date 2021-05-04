EduSense Class processing
================
There are two different modes to process class videos: online and backfill. In online processing mode, the pipeline processes video on the fly, directly fetching video and audio from the ip cameras. For backfill mode, the pipeline grabs video frames from local video files. The processed data is sent to a backend storage server.

To run processing scripts users should have -:

1) Pre-built images for the [pipeline components](/compute). These prebuilt images should be named, following fixed semantics-: 

edusense/video:userName for video, 
edusense/audio:userName for audio and edusense/openpose:userName for openpose.

<b>Note-:</b> developer should use the same userName for all the three docker images. 

2) A running instance of storage server. Refer [storage](/storage) for setting-up guide.

<b>Note-:</b> The script assumes a default SSL setup for storage server. [This can be changed manually] 

## EduSense Backfilling
```
python3 run_backfill.py \
--front_video <student facing video> \ 
--back_video  <instructor facing video> \
--video_dir <video_dir: path of the video directory> \
--keyword <keyword:to identify the video, in the storage server> \
--front_num_gpu_start <starting index of the GPU, that the user wishes to assign to the front video docker eg-:0 > \ 
--front_num_gpu <number of GPU's to be assigned to the front video docker eg-: 1>  \
--back_num_gpu_start <starting index of the GPU, that the user wishes to assign to the back video docker eg-: 1> \
--back_num_gpu <number of GPU's to be assigned to the back video docker eg-: 1> \ 
--time_duration <timeout for the backfill processing> \
--video_schema classinsight-graphql-video \
--audio_schema classinsight-graphql-audio \
--process_real_time \
--backend_url <HTTPS URL of the backend storage server> \
--developer <userName for the docker images (refer the above paragraph)> \
```
