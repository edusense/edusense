import time
import os
import base64
import traceback
import sys
import requests
import json
from datetime import datetime,timedelta

backend_params = None
app_username = os.getenv("EDUSENSE_ANALYTICS_USERNAME", "")
app_password = os.getenv("EDUSENSE_ANALYTICS_PASSWORD", "")
app_url = os.getenv("EDUSENSE_ANALYTICS_URL", "")
    
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
    'id': '11',
    'keyword': 'keywordTest',
    'metaInfo': {
        'pipelineVersion': "keywordTest",
        'analysisStartTime': None,
        'totalRuntime': 0.1,
        'RunModules': ['1'],
        'ModuleRuntime': [],
        'SuccessModules': ['1'],  # left general for now, need to make it strict like
        'FailureModules': ['1'],  # Or('audio', 'gaze', 'location', 'posture', None)
    },
    'debugInfo': '',
    # 'secondLevel': [{
        # 'secondInfo': {
        #     'unixSeconds': 1,
        #     'frameStart': 1,
        #     'frameEnd': 1,
        # },
        # 'audio':{
        #     'isSilence': True,
        #     'isObjectNoise': True,
        #     'isTeacherOnly': True,
        #     'isSingleSpeaker': True,
        # },
        # 'gaze': {
        #     'instructor': {
        #         'angle': 0.1,
        #         'angleChange': 0.2,
        #         'direction': 'left',
        #         'viewingSectorThreshold': 0.0,
        #         'countStudentsInGaze': 0,
        #         'towardsStudents': True,
        #         'lookingDown': True,
        #     },
        #     'student': {
        #         'id': [1],
        #         'angle': [0.1],
        #         'angleChange': [0.1],
        #         'direction': ['left'],
        #         'towardsInstructor': [True],
        #         'lookingDown': [True],
        #         'lookingFront': [True],
        #     },
        # },
        # 'location': {
        #     'instructor': {
        #         'atBoard': True,
        #         'atPodium': True,
        #         'isMoving': True,
        #         'locationCoordinates': [1],
        #         'locationCategory': 'left',
        #         'locationEntropy': 0.1,
        #         'headEntropy': 0.1
        #     },
        #     'student': {
        #         'id': [1],
        #         'trackingIdMap': [[1]],
        #         'isMoving': [True],
        #         'locationCoordinates': [[1]],
        #         'locationCategory':  ['left'],
        #         'locationEntropy': [0.1],
        #         'headEntropy': [0.1],
        #     }
        # },
        # 'posture': {
        #     'instructor': {
        #         'isStanding': True,
        #         'isPointing': True,
        #         'pointingDirection': [0.1],
        #         'handPosture': '0',
        #         'headPosture': '0',
        #         'centroidFaceDistance': 0.1,
        #         'centroidFaceDistanceAbsolute': 0.1,
        #     },
        #     'student': {
        #         'id': [1],
        #         'isStanding': [True],
        #         'bodyPosture': ['test_string'],  # sit straight/ sit slouch/ stand
        #         'headPosture': ['test_string'],  # looking up or not
        #         'handPosture': ['test_string']  # raised, ontable, onface, down, crossed
        #     }
        # },
    #     'crossModal': 'test_string'
    # }]
    'blockLevel': [{
        'blockInfo': {
            'unixStartSeconds': 3,
            'blockLength': 3,
            'id': 3,
        },
        # 'audio':{
        #     'audioBasedActivityType': ['type1', 'type2', 'type3'],
        #     'audioBasedActivityFraction': [0.1, 0.2, 0.3],
        #     'audioBasedActivityBlocks': [[[1, 2], [3, 4]], [[4, 5], [6, 7]]]
        # },
        'gaze': {
            'instructor': {
                'gazeCategory': "gazeCategory1",
                'totalCategoryFraction': [0.01, 0.02, 0.03],
                'longestCategoryFraction': [0.01, 0.02, 0.03],
            },
            'student': {
                'id': [0, 1, 2],
                'numOccurencesInBlock': [0, 1, 2],
                'gazeCategory': ["gazeCategory1", "gazeCategory2", "gazeCategory3"],
                'totalCategoryFraction': [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]],
                'longestCategoryFraction': [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
            },
        },
        # 'location': {
        #     'instructor': {
        #         'atBoard': True,
        #         'atPodium': True,
        #         'isMoving': True,
        #         'locationCoordinates': [1],
        #         'locationCategory': 'left',
        #         'locationEntropy': 0.1,
        #         'headEntropy': 0.1
        #     },
        #     'student': {
        #         'id': [1],
        #         'trackingIdMap': [[1]],
        #         'isMoving': [True],
        #         'locationCoordinates': [[1]],
        #         'locationCategory':  ['left'],
        #         'locationEntropy': [0.1],
        #         'headEntropy': [0.1],
        #     }
        # },
        # 'posture': {
        #     'instructor': {
        #         'isStanding': True,
        #         'isPointing': True,
        #         'pointingDirection': [0.1],
        #         'handPosture': '0',
        #         'headPosture': '0',
        #         'centroidFaceDistance': 0.1,
        #         'centroidFaceDistanceAbsolute': 0.1,
        #     },
        #     'student': {
        #         'id': [1],
        #         'isStanding': [True],
        #         'bodyPosture': ['test_string'],  # sit straight/ sit slouch/ stand
        #         'headPosture': ['test_string'],  # looking up or not
        #         'handPosture': ['test_string']  # raised, ontable, onface, down, crossed
        #     }
        # },
        'crossModal': 'test_string'
    }]
}


query = '''
        {
            analytics(sessionId: "610f3eb7e81eb70c26d9f4b8") {
                id
                keyword
                metaInfo {
                    pipelineVersion
                }
            }
        }
        '''

try:
    # Enter frame data
    # resp = requests.post("http://localhost:9000/sessions/6053a21fdab4eb7dcb32773d/audio/frames/xxx/student/",
    #                         headers=backend_params['headers'],
    #                         json={'frames': [frame_data]})
    
    # Enter Analytics data
    # resp = requests.post("https://edusense-dev-1.andrew.cmu.edu:9000/analytics",
    #                         headers=backend_params['headers'],
    #                         json={'analytics': analytics_schema})

    # Query
    req = {'query': query}
    # resp = requests.post("https://edusense-dev-1.andrew.cmu.edu:9000/query", headers=backend_params['headers'], json=req)
    resp = requests.post(f"http://{app_url}/query", headers=backend_params['headers'],
                         json=req)
    
    print("****resp returned")
    if (resp.status_code != 200 or
        'success' not in resp.json().keys() or
            not resp.json()['success']):
        raise RuntimeError(resp.text)
    
    response = dict(resp.json())
    print(response)

    db_post_time = time.time() - db_post_start_time

    print('db_posting, %f' % db_post_time)

except Exception as e:
    print("*****exception thrown")
    traceback.print_exc(file=sys.stdout)
