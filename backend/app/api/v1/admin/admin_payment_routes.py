from flask import Blueprint, jsonify


admin_payment_bp = Blueprint("admin_payments", __name__)


@admin_payment_bp.get("/")
def get_admin_payments_status():
    return jsonify({"module": "admin_payments", "status": "not_implemented"}), 200
