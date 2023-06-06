"""
Initialize handlers for edusense runtime
"""
# Video handlers
from .VideoHandler import *
from .TrackingHandler import run_tracking_handler
from .PoseHandler import run_pose_handler
from .FaceDetectionHandler import *
from .FaceEmbeddingHandler import *
from .GazeHandler import *

# Output Handlers
from .OutputHandler import *
