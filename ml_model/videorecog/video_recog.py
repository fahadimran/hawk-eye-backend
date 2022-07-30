from app import db
from models.alert import Alert, AlertSchema
from utils.validators import path_exists
from utils.image_utils import (
    convert_to_rgb,
    draw_annotation,
    draw_bounding_box
)
from faceRecognition.facerecog import FaceRecognition
from faceDetector_models.opencvDetector import FaceDetectorOpenCV
from faceDetector_models.mtcnnDetector import FaceDetectorMTCNN
from faceDetector_models.dlibDetector import FaceDetectorDlib
from utils.exceptions import NoNameProvided, PathNotFound
import sys
import time
import traceback
from typing import Dict, List
import os
import cv2
import numpy as np
from datetime import datetime
import uuid


current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append("..")


class FaceRecognitionVideo:

    def __init__(
        self,
        face_detector: str = "dlib",
        model_loc: str = "faceDetector_models_files",
        persistent_db_path: str = "data_file/facial_data.json",
        face_detection_threshold: float = 0.5,
    ) -> None:

        self.face_recognizer = FaceRecognition(
            model_loc=model_loc,
            persistent_data_loc=persistent_db_path,
            face_detection_threshold=face_detection_threshold,
            face_detector=face_detector,
        )
        if face_detector == "opencv":
            self.face_detector = FaceDetectorOpenCV(
                model_loc=model_loc, crop_forehead=True, shrink_ratio=0.2
            )
        elif face_detector == "mtcnn":
            self.face_detector = FaceDetectorMTCNN(
                crop_forehead=True, shrink_ratio=0.2)
        elif face_detector == "dlib":
            self.face_detector = FaceDetectorDlib()

    def recognize_face_video(
        self,
        ws,
        video_path: str = None,
        detection_interval: int = 15,
        save_output: bool = False,
        preview: bool = False,
        output_path: str = "data/output.mp4",
        resize_scale: float = 0.5,
        verbose: bool = True,

    ) -> None:

        if video_path is None:
            # If no video source is given, try
            # switching to webcam
            video_path = 0
        elif not path_exists(video_path):
            raise FileNotFoundError

        cap, video_writer = None, None

        try:
            cap = cv2.VideoCapture(video_path)

            if (cap is None or not cap.isOpened()):
                ws.send("Camera error")

            frame_num = 1
            matches, name, match_dist = [], None, None

            t1 = time.time()

            detectedNames = []

            ws.send("Connected OK")

            while True:
                status, frame = cap.read()
                print(status)

                if not status:
                    break

                try:
                    # Flip webcam feed so that it looks mirrored
                    if video_path == 0:
                        frame = cv2.flip(frame, 2)

                        smaller_frame = convert_to_rgb(
                            cv2.resize(frame, (0, 0),
                                       fx=resize_scale, fy=resize_scale)
                        )

                        matches = self.face_recognizer.recognize_faces(
                            image=smaller_frame, threshold=0.5, bboxes=None
                        )

                    if verbose:
                        if matches != 0:
                            print(matches)
                            for face_bbox, match, dist in matches:

                                id = match["case_id"]
                                self.annotate_facial_data(
                                    matches, frame, resize_scale)
                                if id not in detectedNames:
                                    detectedNames.append(id)
                                    print(id)
                                    now = datetime.now()

                                    # Add new alert to database
                                    alert = Alert(alert_id=uuid.uuid1(),
                                                  case_id=id, status="active", date_generated=now.strftime("%d/%m/%Y %H:%M:%S"), date_closed="", closed_by="", reason_closure="", comments="")

                                    print(alert)
                                    db.session.add(alert)
                                    db.session.commit()

                                    ws.send("Alert Saved")

                    if preview:
                        cv2.imshow("Preview", cv2.resize(frame, (680, 480)))

                    key = cv2.waitKey(50) & 0xFF
                    if key == ord("q"):
                        break
                except Exception:
                    pass
                frame_num += 1

            t2 = time.time()
            print("Time:{}".format((t2 - t1) / 60))
            print("Total frames: {}".format(frame_num))
            print("Time per frame: {}".format((t2 - t1) / frame_num))
            ws.send("Camera Disconnect")

        except Exception as exc:
            raise exc
        finally:
            cv2.destroyAllWindows()
            cap.release()

    def register_face_path(self, img_path: str, name: str) -> None:
        if not path_exists(img_path):
            raise PathNotFound
        try:
            img = cv2.imread(img_path)
            facial_data = self.face_recognizer.register_face(
                image=convert_to_rgb(img), name=name
            )
            if facial_data:
                return True
            return False
        except Exception as exc:
            raise exc

    def annotate_facial_data(
        self, matches: List[Dict], image, resize_scale: float
    ) -> None:
        for face_bbox, match, dist in matches:
            name = match["name"] if match is not None else "Unknown"
            # match_dist = '{:.2f}'.format(dist) if dist < 1000 else 'INF'
            # name = name + ', Dist: {}'.format(match_dist)
            # draw face labels

            draw_annotation(image, name, int(
                1 / resize_scale) * np.array(face_bbox))
