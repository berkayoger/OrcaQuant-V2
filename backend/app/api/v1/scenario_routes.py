from flask import Blueprint, jsonify


scenario_bp = Blueprint("scenario", __name__)


@scenario_bp.get("/")
def get_scenario_status():
    return jsonify({"module": "scenario", "status": "not_implemented"}), 200
