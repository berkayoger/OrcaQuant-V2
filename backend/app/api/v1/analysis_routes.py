from flask import Blueprint, jsonify


analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.get("/")
def get_analysis_status():
    return jsonify({"module": "analysis", "status": "not_implemented"}), 200
