import imp
from flask import Blueprint
from flask import request, jsonify
from flask_jwt_extended import create_access_token, unset_jwt_cookies
from models import Admin
from app import db
from app import bcrypt
import uuid
from api.authorized_user.authorized_user import AuthorizedUser, AuthorizedUserSchema

auth_blueprint = Blueprint('auth', __name__)


# Error handler for 500 Internal server errors
@auth_blueprint.errorhandler(500)
def server_error(e):
    response = {
        "msg": "Something went wrong"
    }

    return response, 500


@auth_blueprint.route("/token", methods=["POST"])
def create_token():

    email = request.json.get("email", None)
    password = request.json.get("password", None)

    s = db.session()
    admin = s.query(Admin).filter(Admin.email.in_(
        [email])).first()

    if (admin == None):
        return {"msg": "Wrong email or password"}, 400

    if (bcrypt.check_password_hash(admin.password, password) == False):
        return {"msg": "Wrong email or password"}, 400

    admin_id = admin.id
    access_token = create_access_token(identity=admin_id)
    return {"access_token": access_token}, 200


@auth_blueprint.route("/register", methods=["POST"])
def create_user():

    user_id = uuid.uuid1()
    fullName = request.json.get("fullName", None)
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    organization = request.json.get("organization", None)
    contact = request.json.get("contact", None)

    s = db.session()
    admin = s.query(Admin).filter(Admin.email.in_(
        [email])).first()

    if (admin):
        return {"msg": "The email address already exists"}, 400

    password = bcrypt.generate_password_hash(password).decode('utf8')
    data = Admin(user_id, fullName, email, password, organization, contact)

    s.add(data)
    s.commit()

    access_token = create_access_token(identity=user_id)
    return {"access_token": access_token}, 200


@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@auth_blueprint.route("/user/login", methods=["POST"])
def create_user_token():

    email = request.json.get("email", None)
    password = request.json.get("password", None)

    s = db.session()
    user = s.query(AuthorizedUser).filter(AuthorizedUser.email.in_(
        [email])).first()

    if (user == None):
        return {"msg": "Wrong email or password"}, 400

    if (bcrypt.check_password_hash(user.password, password) == False):
        return {"msg": "Wrong email or password"}, 400

    user_id = user.id
    access_token = create_access_token(identity=user_id)
    return {"access_token": access_token}, 200
