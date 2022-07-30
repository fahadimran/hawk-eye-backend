from utils.validators import is_valid_img, path_exists
from utils.image_utils import convert_to_dlib_rectangle
from faceDetector_models.opencvDetector import FaceDetectorOpenCV
from faceDetector_models.mtcnnDetector import FaceDetectorMTCNN
from faceDetector_models.dlibDetector import FaceDetectorDlib
from data.data_storage import FaceDataStore
from utils.exceptions import (
    FaceMissing,
    InvalidImage,
    ModelFileMissing,
    NoFaceDetected,
    NoNameProvided,
)
import os
import sys
import uuid
from typing import Dict, List, Tuple
import dlib
import numpy as np

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


class FaceRecognition:

    keypoints_model_path = "shape_predictor_5_face_landmarks.dat"
    face_recog_model_path = "dlib_face_recognition_resnet_model_v1.dat"

    def __init__(
            self,
            model_loc: str = "faceDetector_models_files",
            persistent_data_loc="ml_model/data_file/facial_data_db.json",
            face_detection_threshold: int = 0.5,
            face_detector: str = "dlib",
    ) -> None:

        keypoints_model_path = os.path.join(
            model_loc, FaceRecognition.keypoints_model_path
        )
        dir = os.getcwd() + '\\ml_model'

        keypoints_model_path = os.path.join(
            dir, keypoints_model_path
        )

        face_recog_model_path = os.path.join(
            model_loc, FaceRecognition.face_recog_model_path
        )
        face_recog_model_path = os.path.join(
            dir, face_recog_model_path
        )

        if not (
                path_exists(keypoints_model_path) or path_exists(
                    face_recog_model_path)
        ):
            raise ModelFileMissing
        if face_detector == "opencv":
            self.face_detector = FaceDetectorOpenCV(
                model_loc=model_loc, crop_forehead=True, shrink_ratio=0.2
            )
        elif face_detector == "mtcnn":
            self.face_detector = FaceDetectorMTCNN(
                crop_forehead=True, shrink_ratio=0.2)
        else:
            self.face_detector = FaceDetectorDlib()
        persistent_data_loc = os.path.join(dir, persistent_data_loc)

        self.face_detection_threshold = face_detection_threshold

        self.keypoints_detector = dlib.shape_predictor(keypoints_model_path)
        self.face_recognizor = dlib.face_recognition_model_v1(
            face_recog_model_path)
        self.datastore = FaceDataStore()

    def register_face(self, image=None, name: str = None, case_id: str = None, bbox: List[int] = None):

        if not is_valid_img(image) or name is None:
            raise NoNameProvided if name is None else InvalidImage

        image = image.copy()
        face_encoding = None

        try:
            if bbox is None:
                bboxes = self.face_detector.detect_faces(image=image)
                if len(bboxes) == 0:
                    raise FaceMissing
                bbox = bboxes[0]
            face_encoding = self.get_facial_fingerprint(image, bbox)

            # Convert the numpy array to normal python float list
            # to make json serialization simpler
            facial_data = {
                "id": str(uuid.uuid1()),
                "encoding": tuple(face_encoding.tolist()),
                "name": name,
                "case_id": case_id
            }
            # save the encoding with the name
            self.save_facial_data(facial_data)

        except Exception as exc:
            raise exc
        return facial_data

    def save_facial_data(self, facial_data: Dict = None) -> bool:

        if facial_data is not None:
            self.datastore.add_facial_data(facial_data=facial_data)
            return True
        return False

    def get_registered_faces(self) -> List[Dict]:

        return self.datastore.get_all_facial_data()

    def recognize_faces(
            self, image, threshold: float = 0.5, bboxes: List[List[int]] = None
    ):

        if image is None:
            return InvalidImage
        image = image.copy()

        if bboxes is None:
            bboxes = self.face_detector.detect_faces(image=image)
        if len(bboxes) == 0:
            return 0
        # Load the data of existing registered faces
        # compare using the metric the closest match
        all_facial_data = self.datastore.get_all_facial_data()
        matches = []
        for bbox in bboxes:
            face_encoding = self.get_facial_fingerprint(image, bbox)
            match, min_dist = None, 10000000
            for face_data in all_facial_data:
                dist = self.euclidean_distance(
                    face_encoding, face_data["encoding"])
                if dist <= threshold and dist < min_dist:
                    match = face_data
                    min_dist = dist
            # bound box, matched face details, dist from closest match
            if match is not None:
                matches.append((bbox, match, min_dist))
        return matches

    def get_facial_fingerprint(self, image, bbox: List[int] = None) -> List[float]:

        if bbox is None:
            raise FaceMissing
        # Convert to dlib format rectangle
        bbox = convert_to_dlib_rectangle(bbox)
        # Get the facial landmark coordinates
        face_keypoints = self.keypoints_detector(image, bbox)

        face_encoding = self.get_face_encoding(image, face_keypoints)
        return face_encoding

    def get_face_encoding(self, image, face_keypoints: List):

        encoding = self.face_recognizor.compute_face_descriptor(
            image, face_keypoints, 1
        )
        return np.array(encoding)

    def euclidean_distance(self, vector1: Tuple, vector2: Tuple):

        return np.linalg.norm(np.array(vector1) - np.array(vector2))
