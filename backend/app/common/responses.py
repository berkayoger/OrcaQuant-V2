from flask import jsonify


def ok(data: dict | list | None = None, status: int = 200):
    return jsonify({"ok": True, "data": data}), status


def created(data: dict | list | None = None):
    return jsonify({"ok": True, "data": data}), 201


def error_response(code: str, message: str, status: int = 400):
    return jsonify({"ok": False, "error": {"code": code, "message": message}}), status
