"""Auth routes skeleton for V1 migration."""
from flask import Blueprint, jsonify

auth_v2_bp = Blueprint("auth_v2", __name__)


@auth_v2_bp.get("/status")
def auth_status() -> tuple[dict[str, str], int]:
    """Return placeholder auth module status."""
    return {"module": "auth", "status": "skeleton"}, 200
