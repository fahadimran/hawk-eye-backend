import os
import sys
from typing import List

import cv2

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from utils.exceptions import InvalidImage, ModelFileMissing
from utils.validators import is_valid_img
from abstract_classes.detector import FaceDetector

class FaceDetectorOpenCV(FaceDetector):


    def __init__(
        self, model_loc="faceDetector_models_files", crop_forehead: bool = True, shrink_ratio: int = 0.1
    ):

        # Model file and associated config path
        model_path = os.path.join(model_loc, "opencv_face_detector_uint8.pb")
        config_path = os.path.join(model_loc, "opencv_face_detector.pbtxt")

        dir = os.getcwd()
        base_path, path = os.path.split(dir)
        model_path = os.path.join(base_path, model_path)
        config_path = os.path.join(base_path, config_path)
        self.crop_forehead = crop_forehead
        self.shrink_ratio = shrink_ratio
        if not os.path.exists(model_path) or not os.path.exists(config_path):
            raise ModelFileMissing
        try:
            # load the model
            self.face_detector = cv2.dnn.readNetFromTensorflow(model_path, config_path)
        except Exception as e:
            raise e

    def model_inference(self, image) -> List:

        img_blob = cv2.dnn.blobFromImage(
            image, 1.0, (300, 300), [104, 117, 123], False, False
        )
        # Feed the input blob to NN and get the output layer predictions
        self.face_detector.setInput(img_blob)
        detections = self.face_detector.forward()

        return detections

    def detect_faces(self, image, conf_threshold: float = 0.5) -> List[List[int]]:

        if not is_valid_img(image):
            raise InvalidImage

        image = image.copy()
        height, width = image.shape[:2]

        detections = self.model_inference(image)
        bboxes = []
        if detections is not None:
            for idx in range(detections.shape[2]):
                conf = detections[0, 0, idx, 2]
                if conf >= conf_threshold:
                    # Scale the bbox coordinates to suit image
                    x1 = int(detections[0, 0, idx, 3] * width)
                    y1 = int(detections[0, 0, idx, 4] * height)
                    x2 = int(detections[0, 0, idx, 5] * width)
                    y2 = int(detections[0, 0, idx, 6] * height)

                    if self.crop_forehead:
                        y1 = y1 + int(height * self.shrink_ratio)

                    if self.is_valid_bbox([x1, y1, x2, y2], height, width):
                        bboxes.append([x1, y1, x2, y2])
        if bboxes is not None:
            return bboxes

    def is_valid_bbox(self, bbox: List[int], height: int, width: int) -> bool:

        for idx in range(0, len(bbox), 2):
            if bbox[idx] < 0 or bbox[idx] >= width:
                return False
        for idx in range(1, len(bbox), 2):
            if bbox[idx] < 0 or bbox[idx] >= height:
                return False
        return True

    def __repr__(self):
        return "FaceDetectorOPENCV <model_loc=str>"


