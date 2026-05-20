from flask import Blueprint, jsonify
from sqlalchemy import text

from app.extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.get("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200


@health_bp.get("/readyz")
def readyz():
    checks = {"database": "ok"}

    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        checks["database"] = "error"
        return jsonify({"status": "error", "checks": checks}), 503

    return jsonify({"status": "ok", "checks": checks}), 200
