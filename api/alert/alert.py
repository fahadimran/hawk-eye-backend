from datetime import datetime
from flask import Blueprint, jsonify, request
from models import RegisteredCase, Alert, RegisteredCaseSchema, AlertSchema
from models import AlertSchema
from app import db
from flask_jwt_extended import jwt_required


alert_blueprint = Blueprint("alerts", __name__)

# Error handler for 500 Internal server errors


@alert_blueprint.errorhandler(500)
def server_error(e):
    response = {
        "msg": "Something went wrong"
    }

    return response, 500


@alert_blueprint.route("/active/<alert_id>", methods=["GET"])
@jwt_required()
def active_alert_details(alert_id):

    s = db.session()

    alert_id = alert_id
    alert_details = s.query(Alert).filter(Alert.alert_id.in_(
        [alert_id])).first()

    case_details = s.query(RegisteredCase).filter(RegisteredCase.case_id.in_(
        [alert_details.case_id])).first()

    case_schema = RegisteredCaseSchema()
    output = case_schema.dump(case_details)

    return jsonify({"case_details": output, "alert_date": alert_details.date_generated})


@alert_blueprint.route("/active", methods=["GET"])
@jwt_required()
def get_active_alerts():

    s = db.session()

    active_alerts = s.query(Alert).filter(Alert.status.in_(["active"])).all()
    alerts_schema = AlertSchema(many=True)
    output = alerts_schema.dump(active_alerts)

    return jsonify({"active_alerts": output})


@alert_blueprint.route("/history", methods=["GET"])
@jwt_required()
def get_closed_alerts():

    s = db.session()

    closed_alerts = s.query(Alert).filter(Alert.status.in_(["closed"])).all()
    alerts_schema = AlertSchema(many=True)
    output = alerts_schema.dump(closed_alerts)

    return jsonify({"closed_alerts": output})


@alert_blueprint.route("/history/<alert_id>", methods=["GET"])
@jwt_required()
def closed_alert_details(alert_id):

    s = db.session()

    alert_id = alert_id
    alert_details = s.query(Alert).filter(Alert.alert_id.in_(
        [alert_id])).first()

    alerts_schema = AlertSchema()
    output = alerts_schema.dump(alert_details)

    return jsonify({"alert_details": output})


@alert_blueprint.route("/close/<alert_id>", methods=["GET"])
@jwt_required()
def close_alert_details(alert_id):

    s = db.session()

    alert_id = alert_id
    alert_details = s.query(Alert).filter(Alert.alert_id.in_(
        [alert_id])).first()

    alerts_schema = AlertSchema()
    output = alerts_schema.dump(alert_details)

    results = {"case_id": output["case_id"],
               "date_generated": output["date_generated"]}

    return jsonify({"alert_details": results})


@alert_blueprint.route("/close/<alert_id>", methods=["PUT"])
@jwt_required()
def close_alert(alert_id):

    closed_by = request.json.get("person_name", None)
    reason_closure = request.json.get("reason_closure", None)
    comments = request.json.get("comments", None)
    now = datetime.now()

    s = db.session()

    alert_id = alert_id
    alert_details = s.query(Alert).filter(Alert.alert_id.in_(
        [alert_id])).first()

    alert_details.status = "closed"
    alert_details.closed_by = closed_by
    alert_details.reason_closure = reason_closure
    alert_details.comments = comments
    alert_details.date_closed = now.strftime("%d/%m/%Y %H:%M:%S")

    s.add(alert_details)
    s.commit()

    return jsonify({"msg": "Alert closed successfully"}), 200
