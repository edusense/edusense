EduSense Class processing
================
There are two different modes to process class videos: online and backfill. In online processing mode, the pipeline processes video on the fly, directly fetching video and audio from the ip cameras. For backfill mode, the pipeline grabs video frames from local video files. The processed data is sent to a backend storage server.

To run processing scripts users should have -:

1) Pre-built images for each [pipeline components](/compute) .These prebuilt images should be named, following a fixed semantic edusense/video:userName for video, 
edusense/audio:userName for audio and edusense/openpose:userName for openpose.
<b>Note-:</b> user should use the same userName for all the three docker images 

2) A running storage server. Refer [storage](/storage) for setting-up guide.

<b>Note-:</b> The script assumes a default SSL setup for storage server. [This can be changed manually] 

## EduSense Backfilling
```
python3 run_backfill.py \
--front_video <student facing video> \
--back_video  <instructor facing video> \
--video_dir <video_dir: path of the video directory> \
--keyword classinsight-cmu_88888D_407sc_104_201808301210 

--front_num_gpu_start 0 --front_num_gpu 1 --back_num_gpu_start 1 --back_num_gpu 1 --time_duration 60 --video_schema classinsight-graphql-video --audio_schema classinsight-graphql-audio --process_real_time --backend_url edusense-dev-1.andrew.cmu.edu:3000 --developer pranav --log_dir /home/pranav/logs






```

