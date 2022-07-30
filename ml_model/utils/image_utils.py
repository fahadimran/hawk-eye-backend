from typing import List, Tuple
import os
import sys
import cv2
import dlib
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from utils.exceptions import InvalidImage
from utils.validators import is_valid_img


def convert_to_rgb(image):

    if not is_valid_img(image):
        raise InvalidImage
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def convert_to_dlib_rectangle(bbox):

    return dlib.rectangle(bbox[0], bbox[1], bbox[2], bbox[3])


def load_image_path(img_path, mode: str = "rgb"):

    try:
        img = cv2.imread(img_path)
        if mode == "rgb":
            return convert_to_rgb(img)
        return img
    except Exception as exc:
        raise exc


def draw_bounding_box(image, bbox: List[int], color: Tuple = (0, 255, 0)):

    x1, y1, x2, y2 = bbox
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
    return image


def draw_annotation(image, name: str, bbox: List[int], color: Tuple = (0, 255, 0)):

    draw_bounding_box(image, bbox, color=color)
    x1, y1, x2, y2 = bbox

    # Draw the label with name below the face
    cv2.rectangle(image, (x1, y2 - 20), (x2, y2), color, cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(image, name, (x1 + 6, y2 - 6), font, 0.6, (0, 0, 0), 2)


def get_facial_ROI(image, bbox: List[int]):

    if image is None or bbox is None:
        raise InvalidImage if image is None else ValueError
    return image[bbox[1] : bbox[3], bbox[0] : bbox[2], :]


