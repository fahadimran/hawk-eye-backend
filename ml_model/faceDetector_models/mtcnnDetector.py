import sys
from typing import List
import os

from mtcnn import MTCNN


current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from utils.exceptions import InvalidImage
from utils.validators import is_valid_img
from abstract_classes.detector import FaceDetector


class FaceDetectorMTCNN(FaceDetector):

    def __init__(self, crop_forehead: bool = True, shrink_ratio: int = 0.1):

        try:
            # load the model
            self.face_detector = MTCNN()
            self.crop_forehead = crop_forehead
            self.shrink_ratio = shrink_ratio

        except Exception as e:
            raise e

    def detect_faces(self, image, conf_threshold: float = 0.5) -> List[List[int]]:

        if not is_valid_img(image):
            raise InvalidImage

        # Do a forward propagation with the blob created from input img
        detections = self.face_detector.detect_faces(image)
        # Bounding box coordinates of faces in image
        bboxes = []
        for _, detection in enumerate(detections):
            conf = detection["confidence"]
            if conf >= conf_threshold:
                x, y, w, h = detection["box"]
                x1, y1, x2, y2 = x, y, x + w, y + h
                # Trim forehead area to match dlib style facial ROI
                if self.crop_forehead:
                    y1 = y1 + int(h * self.shrink_ratio)
                bboxes.append([x1, y1, x2, y2])

        return bboxes

    def __repr__(self):
        return "FaceDetectorMTCNN"
