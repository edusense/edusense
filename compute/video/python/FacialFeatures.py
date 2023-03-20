'''
Comparing facial features for tracking face for a given session and across sessions
'''
from deepface import DeepFace
import glob
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from deepface.commons import functions, realtime, distance as dst
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

face_recognition_models = [
  "VGG-Face",
  "Facenet",
  "Facenet512",
  "OpenFace",
  "DeepFace",
  "DeepID",
  "ArcFace",
  "Dlib",
  "SFace",
]

face_detection_backends = [
  'opencv',
  'ssd',
  'dlib',
  'mtcnn',
  'retinaface',
  'mediapipe'
]

dissimilarity_metrics = ["cosine", "euclidean", "euclidean_l2"]

frame_dir = '/Users/ppatida2/Edusense/edusense/cache/frames'
faces_all = []
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
resnet_facedetect = InceptionResnetV1(pretrained='vggface2').eval().to(device)
mtcnn = MTCNN(
    image_size=224, margin=0, min_face_size=20,
    thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
    device=device
)

for img in glob.glob(f'{frame_dir}/*'):
  print(img)
  faces = DeepFace.extract_faces(img, detector_backend='retinaface')
  dfs = DeepFace.represent(img, detector_backend='retinaface',enforce_detection=False)

  img_embedding = resnet_facedetect(torch.from_numpy(np.copy(faces[3]['face'])).permute(2,0,1).unsqueeze(0))
  faces_all+=[xr['embedding'] for xr in dfs]
  print(f"count faces: {len(dfs)}")

faces_all=np.array(faces_all)
faces_mat = np.zeros((faces_all.shape[0],faces_all.shape[0]))
threshold = dst.findThreshold('retinaface','euclidean_l2')
for i in range(faces_all.shape[0]):
  for j in range(faces_all.shape[0]):
    faces_mat[i][j]  =dst.findEuclideanDistance(
                    dst.l2_normalize(faces_all[i,:]), dst.l2_normalize(faces_all[j,:])
                )
    faces_mat[i][j] = faces_mat[i][j]<=threshold
plt.imshow(faces_mat[:10,:10])
plt.show()
print("Finished")

