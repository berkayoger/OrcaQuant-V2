from flask import Blueprint, jsonify


docs_bp = Blueprint("docs", __name__)


@docs_bp.get("/")
def get_docs_status():
    return jsonify({"module": "docs", "status": "not_implemented"}), 200
