from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from models import RegisteredCase, Alert, RegisteredCaseSchema, AlertSchema
from models import AlertSchema
from app import db
from flask_jwt_extended import jwt_required

from models.authorized_user import AuthorizedUser


stats_blueprint = Blueprint("stats", __name__)

# Error handler for 500 Internal server errors


@stats_blueprint.errorhandler(500)
def server_error(e):
    response = {
        "msg": "Something went wrong"
    }

    return response, 500


@stats_blueprint.route("/", methods=["GET"])
@jwt_required()
def get_stats():

    s = db.session()

    active_alerts_count = s.query(Alert).filter(
        Alert.status.in_(["active"])).count()
    closed_alerts_count = s.query(Alert).filter(
        Alert.status.in_(["closed"])).count()
    registered_cases_count = s.query(RegisteredCase).count()
    authorized_users_count = s.query(AuthorizedUser).count()

    s.commit()

    return jsonify({"count_active": active_alerts_count, "count_closed": closed_alerts_count,
                    "registered_cases_count": registered_cases_count, "authorized_users_count": authorized_users_count}), 200
