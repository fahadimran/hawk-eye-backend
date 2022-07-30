import os
import sys
from typing import List

import cv2
import dlib

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from utils.exceptions import InvalidImage, ModelFileMissing
from utils.validators import is_valid_img
from abstract_classes.detector import FaceDetector


class FaceDetectorDlib(FaceDetector):
    cnn_model_filename = "faceDetector_models_files/mmod_human_face_detector.dat"

    def __init__(self, model_loc: str = "models", model_type: str = "hog"):

        try:
            # load the model
            if model_type == "hog":
                pass
                self.face_detector = dlib.get_frontal_face_detector()
            else:
                # MMOD model
                dir = os.getcwd()
                base_path, path = os.path.split(dir)
                cnn_model_path = os.path.join(
                    base_path, FaceDetectorDlib.cnn_model_filename
                )
                if not os.path.exists(cnn_model_path):
                    raise ModelFileMissing
                self.face_detector = dlib.cnn_face_detection_model_v1(cnn_model_path)
            self.model_type = model_type
        except Exception as e:
            raise e

    def detect_faces(self, image, num_upscaling: int = 1) -> List[List[int]]:

        if not is_valid_img(image):
            raise InvalidImage

        lists = []
        if self.face_detector(image, num_upscaling) != "":
            return [
                self.dlib_rectangle_to_list(bbox)
                for bbox in self.face_detector(image, num_upscaling)
            ]
        else:
            return lists

    def dlib_rectangle_to_list(self, dlib_bbox) -> List[int]:

        # if it is MMOD type rectangle
        if type(dlib_bbox) == dlib.mmod_rectangle:
            dlib_bbox = dlib_bbox.rect
        # Top left corner
        x1, y1 = dlib_bbox.tl_corner().x, dlib_bbox.tl_corner().y
        width, height = dlib_bbox.width(), dlib_bbox.height()
        # Bottom right point
        x2, y2 = x1 + width, y1 + height

        return [x1, y1, x2, y2]

    def __repr__(self):
        return "FaceDetectorDlib"



