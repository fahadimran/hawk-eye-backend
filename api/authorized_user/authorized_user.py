import uuid
from flask import Blueprint, jsonify, request
from models import AuthorizedUser, AuthorizedUserSchema
from app import db, bcrypt
from flask_jwt_extended import jwt_required


authorized_user_blueprint = Blueprint("authorized_user", __name__)


# Error handler for 500 Internal server errors
@authorized_user_blueprint.errorhandler(500)
def server_error(e):
    response = {
        "msg": "Something went wrong"
    }

    return response, 500


@authorized_user_blueprint.route("/", methods=["GET"])
@jwt_required()
def get_authorized_users():

    s = db.session()

    authorized_users = s.query(AuthorizedUser).all()

    authorized_user_schema = AuthorizedUserSchema(many=True)
    output = authorized_user_schema.dump(authorized_users)

    return jsonify({"authorized_users": output}), 200


@authorized_user_blueprint.route("/<user_id>", methods=["GET"])
@jwt_required()
def get_authorized_user(user_id):

    user_id = user_id

    s = db.session()

    authorized_user = s.query(AuthorizedUser).filter(AuthorizedUser.id.in_(
        [user_id])).first()

    authorized_user_schema = AuthorizedUserSchema()
    output = authorized_user_schema.dump(authorized_user)

    return jsonify({"authorized_user": output}), 200


@authorized_user_blueprint.route("/edit/<user_id>", methods=["PUT"])
@jwt_required()
def update_authorized_user(user_id):

    user_id = user_id

    s = db.session()

    authorized_user = s.query(AuthorizedUser).filter(AuthorizedUser.id.in_(
        [user_id])).first()

    fullName = request.json.get("fullName", None)
    email = request.json.get("email", None)
    contact = request.json.get("contact", None)
    organization = request.json.get("organization", None)

    # Check email exists
    user_email = s.query(AuthorizedUser).filter(AuthorizedUser.email.in_(
        [email])).first()

    if (user_email and authorized_user.email != email):
        return jsonify({"msg": "Another user exists with the same email"}), 400

    authorized_user.fullName = fullName
    authorized_user.email = email
    authorized_user.organization = organization
    authorized_user.contact = contact

    s.add(authorized_user)
    s.commit()

    return jsonify({"msg":  "User profile updated successfully"}), 201


@authorized_user_blueprint.route("/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_authorized_user(user_id):

    user_id = user_id

    s = db.session()

    s.query(AuthorizedUser).filter(AuthorizedUser.id.in_(
        [user_id])).delete()

    s.commit()

    return jsonify({"msg": "User deleted successfully"}), 201


@authorized_user_blueprint.route("/new", methods=["POST"])
@jwt_required()
def create_authorized_user():

    id = str(uuid.uuid1())
    fullName = request.json.get("fullName", None)
    email = request.json.get("email", None)
    organization = request.json.get("organization", None)
    contact = request.json.get("contact", None)
    password = request.json.get("password", None)

    s = db.session()

    user = s.query(AuthorizedUser).filter(AuthorizedUser.email.in_(
        [email])).first()

    if (user):
        return {"msg": "The email address already exists"}, 400

    password = bcrypt.generate_password_hash(password).decode('utf8')
    data = AuthorizedUser(id, fullName, email, password, organization, contact)

    s.add(data)
    s.commit()

    return jsonify({"msg": "User created successfully"}), 201
