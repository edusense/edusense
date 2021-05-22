import time
import os
import base64
import traceback
import sys
import requests
from datetime import datetime,timedelta

backend_params = None
app_username = os.getenv("APP_USERNAME", "")
app_password = os.getenv("APP_PASSWORD", "")
    
cred = '{}:{}'.format(app_username, app_password).encode('ascii')
encoded_cred = base64.standard_b64encode(cred).decode('ascii')

backend_params = {
    'headers': {
        'Authorization': 'Basic {}'.format(encoded_cred),
        'Content-Type': 'application/json'}
}

db_post_start_time = time.time()
# default_time=timedelta(hours=9,minutes=0)
# default_date="2020-05-28"
# this_time = default_date+'T'+str(default_time)
# print(this_time)
# frame_data = {
#     'frameNumber': 0,
#     'timestamp': "2006-01-02T15:04:05Z",
#     'channel': 'xxx',
#     'analysisData': {
#         'students': [{
#             'posture':{
#                 'upright': True,
#                 'attention': 0.65
#             },
#             'face': {
#                 'emotion': 0.65,
#                 'gaze': 0.65
#             }
#         }],
#         'instructors': [{
#             'posture':{
#                 'upright': False,
#                 'attention': 0.35
#             },
#             'face': {
#                 'emotion': 0.35,
#                 'gaze': 0.35
#             }
#         }]
#     }

# }

# frame_data = {
#     'frameNumber': 76,
#     'timestamp': "2006-01-02T15:04:05Z",
#     'channel': 'xxx',
#     'audio': {
#         'amplitude': 0.0,
#         'melFrequency': [[0.0]],
#         'mfccFeatures': [[0.0]],
#         'polyFeatures': [[0.0]],
#         'inference': {
#             'speech':{
#                 'confidence': 0.0,
#                 'speaker': 'Name'
#             }
#         }
#     },
#     'samplingRate': 0
# }



analytics_schema = {
    'id': '4',
    'keyword': '0',
    # 'metaInfo': {
    #     'pipelineVersion': None,
    #     'analysisStartTime': 1,
    #     'totalRuntime': 0.1,
    #     'RunModules': ['1'],
    #     'ModuleRuntime': [0.1],
    #     'SuccessModules': ['1'],  # left general for now, need to make it strict like
    #     'FailureModules': ['1'],  # Or('audio', 'gaze', 'location', 'posture', None)
    # },
    'metaInfo': None,
    'debugInfo': '',
    # 'secondLevel': [{
    #     'secondInfo': {
    #         'unixSeconds': 0,
    #         'frameStart': 0,
    #         'frameEnd': 0,
    #     },
    #     'audio':{
    #         'isSilence': True,
    #         'isObjectNoise': True,
    #         'isTeacherOnly': True,
    #         'isSingleSpeaker': True,
    #     },
    #     'gaze': {
    #         'instructor': {
    #             'angle': 0.0,
    #             'angleChange': 0.0,
    #             'direction': 'left',
    #             'viewingSectorThreshold': 0.0,
    #             'countStudentsInGaze': 0,
    #             'towardsStudents': True,
    #             'lookingDown': True,
    #         },
    #         'student': {
    #             'id': [0],
    #             'angle': [0.0],
    #             'angleChange': [0.0],
    #             'direction': ['left'],
    #             'towardsInstructor': [True],
    #             'lookingDown': [True],
    #             'lookingFront': [True],
    #         },
    #     },
    #     'location': {
    #         'instructor': {
    #             'atBoard': True,
    #             'atPodium': True,
    #             'isMoving': True,
    #             'locationCoordinates': [0],
    #             'locationCategory': 'left',
    #             'locationEntropy': 0.0,
    #             'headEntropy': 0.0
    #         },
    #         'student': {
    #             'id': [0],
    #             'trackingIdMap': [[0]],
    #             'isMoving': [True],
    #             'locationCoordinates': [[0]],
    #             'locationCategory':  ['left'],
    #             'locationEntropy': [0.0],
    #             'headEntropy': [0.0],
    #         }
    #     },
    #     'posture': {
    #         'instructor': {
    #             'isStanding': True,
    #             'isPointing': True,
    #             'pointingDirection': [0.0],
    #             'handPosture': '0',
    #             'headPosture': '0',
    #             'centroidFaceDistance': 0.0,
    #             'centroidFaceDistanceAbsolute': 0.0,
    #         },
    #         'student': {
    #             'id': [0],
    #             'isStanding': [True],
    #             'bodyPosture': ['0'],  # sit straight/ sit slouch/ stand
    #             'headPosture': ['0'],  # looking up or not
    #             'handPosture': ['0']  # raised, ontable, onface, down, crossed
    #         }
    #     },
    #     'crossModal': '0'
    # }]
}

try:
    # resp = requests.post("http://localhost:3000/sessions/6053a21fdab4eb7dcb32773d/analysis/frames/xxx/student/",
    #                         headers=backend_params['headers'],
    #                         json={'frames': [frame_data]})
    # resp = requests.post("http://localhost:9000/sessions/6053a21fdab4eb7dcb32773d/audio/frames/xxx/student/",
    #                         headers=backend_params['headers'],
    #                         json={'frames': [frame_data]})
    resp = requests.post("https://edusense-dev-1.andrew.cmu.edu:9000/analytics",
                            headers=backend_params['headers'],
                            json={'analytics': analytics_schema})
    print("****resp returned")
    if (resp.status_code != 200 or
        'success' not in resp.json().keys() or
            not resp.json()['success']):
        raise RuntimeError(resp.text)

    db_post_time = time.time() - db_post_start_time

    print('db_posting, %f' % db_post_time)

except Exception as e:
    print("*****exception thrown")
    traceback.print_exc(file=sys.stdout)
