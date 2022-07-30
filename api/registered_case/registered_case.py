from flask import Blueprint, jsonify
from models import RegisteredCase, RegisteredCaseSchema
from app import db


registered_case_blueprint = Blueprint("registered_case", __name__)

# Error handler for 500 Internal server errors


@registered_case_blueprint.errorhandler(500)
def server_error(e):
    response = {
        "msg": "Something went wrong"
    }

    return response, 500


@registered_case_blueprint.route("/<case_id>", methods=["GET"])
def get_case_details(case_id):

    s = db.session()

    case_id = case_id

    case_details = s.query(RegisteredCase).filter(RegisteredCase.case_id.in_(
        [case_id])).first()

    case_schema = RegisteredCaseSchema()
    output = case_schema.dump(case_details)

    return jsonify({"case_details": output})
