from ml_model.videorecog.video_recog import FaceRecognitionVideo
from app import db, app, sock


@sock.route('/alerts')
def real_time_alerts(ws):

    while True:
        data = ws.receive()
        print(data)

        if (data == "Start Monitoring"):
            face_recognizer = FaceRecognitionVideo(face_detector='dlib')

            face_recognizer.recognize_face_video(
                ws, preview=True, video_path=None, detection_interval=2, save_output=True, resize_scale=0.25, verbose=True)
