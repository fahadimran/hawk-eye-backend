from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Admin, AdminSchema, RegisteredCase
from werkzeug.utils import secure_filename
from ml_model.utils.image_utils import load_image_path
from ml_model.faceRecognition.facerecog import FaceRecognition
import os
import uuid
from datetime import datetime


admin_blueprint = Blueprint("admin_blueprint", __name__)


@admin_blueprint.errorhandler(500)
def server_error(e):
    response = {
        "msg": "Something went wrong"
    }

    return response, 500


UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER")
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Error handler for 500 Internal server errors
@admin_blueprint.errorhandler(500)
def server_error(e):
    response = {
        "msg": "Something went wrong"
    }

    return response, 500


@admin_blueprint.route("/profile", methods=["GET", "POST", "PUT"])
@jwt_required()
def my_profile():

    if request.method == "GET":

        s = db.session()

        admin = s.query(Admin).filter(Admin.id.in_(
            [get_jwt_identity()])).first()
        admin_schema = AdminSchema()
        output = admin_schema.dump(admin)

        return jsonify({"admin": output}), 200

    elif request.method == "PUT":

        s = db.session()

        admin = s.query(Admin).filter(Admin.id.in_(
            [get_jwt_identity()])).first()

        fullName = request.json.get("fullName", None)
        contact = request.json.get("contact", None)

        admin.fullName = fullName
        admin.contact = contact

        s.commit()
        admin_schema = AdminSchema()
        output = admin_schema.dump(admin)

        return jsonify({"admin": output}), 200


@admin_blueprint.route("/register-case", methods=["POST"])
def register_case():

    if request.method == "POST":
        target = UPLOAD_FOLDER

        if not os.path.isdir(target):
            os.mkdir(target)

        file = request.files["file"]
        fullName = request.form["name"]
        age = request.form["age"]
        details = request.form["details"]
        crime = request.form["crime"]
        now = datetime.now()

        if file and allowed_file(file.filename):

            # Generate filename using uuid
            generated_name = str(uuid.uuid1())
            extension = file.filename.rsplit(".", 1)[1].lower()
            filename = generated_name + "." + extension
            filename = secure_filename(filename)

            # Save file
            destination = "/".join([target, filename])
            file.save(destination)

            # Add case to db
            s = db.session()

            # Generate Case id
            case_id = str(uuid.uuid1())
            data = RegisteredCase(case_id, fullName, age,
                                  details, crime, filename, now.strftime("%d/%m/%Y %H:%M:%S"))

            s.add(data)
            s.commit()

            # Train model
            face_recognizer = FaceRecognition(
                model_loc="faceDetector_models_files",
                persistent_data_loc="ml_model/data_file/facial_data_db.json",
                face_detector="dlib",
            )

            img = load_image_path(destination)
            face_recognizer.register_face(
                image=img, name=fullName, case_id=case_id)

            return {
                "msg": "New Case registered successfully"
            }, 200
