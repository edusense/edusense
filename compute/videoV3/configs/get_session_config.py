"""
This file generate session running config for edusense pipeline
"""

def get_session_config(source_dir,
                       session_dir,
                       session_keyword,
                       output_dir,
                       device):
    video_config = {
        # videoHandler
        'session_dir':session_dir,
        'session_keyword':session_keyword,
        'source_dir':source_dir,
        'output_dir':output_dir,
        'device':device,
        'video_fps': 5,

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