"""
This file generate session running config for edusense pipeline
"""

def get_session_config(source_dir,
                       course_id,
                       session_dir,
                       session_keyword,
                       session_camera,
                       device,
                       target_fps,
                       start_frame_number=0,
                       frame_interval=0.):
    video_config = {
        # videoHandler
        'course_id':course_id,
        'session_dir':session_dir,
        'session_keyword':session_keyword,
        'source_dir':source_dir,
        'session_camera':session_camera,
        'device':device,
        'target_fps': target_fps,
        'start_frame_number':start_frame_number,
        'frame_interval':frame_interval,

        # trackingHandler
        'track_config':f'{source_dir}/configs/mmlab/ocsort_yolox_x_crowdhuman_mot17-private-half.py',
        'track_checkpoint':f'{source_dir}/models/mmlab/ocsort_yolox_x_crowdhuman_mot17-private-half_20220813_101618-fe150582.pth',

        # poseHandler
        'pose_config':f'{source_dir}/configs/mmlab/hrnet_w32_coco_256x192.py',
        'pose_checkpoint':f'{source_dir}/models/mmlab/hrnet_w32_coco_256x192-c78dce93_20200708.pth',
        'kpt_thr': 0.3,

        # faceDetectionHandler

        # gazeHandler

        # faceEmbeddingHandler
        'face_embedding_model_name':'vggface2',

    }

    audio_config = {
        # audioHandler

        # speechHandler

        # speakerVerificationHandler

    }

    session_config = dict(video_config)
    session_config.update(audio_config)
    return session_config