"""Error handler registration for Flask app."""

from flask import Flask, jsonify
from pydantic import ValidationError as PydanticValidationError

from app.core.errors.exceptions import OrcaQuantError, ValidationError


def _to_payload(error: OrcaQuantError):
    return {"error": {"code": error.error_code, "message": error.message}}


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(OrcaQuantError)
    def _handle_domain_error(error: OrcaQuantError):
        return jsonify(_to_payload(error)), error.status_code

    @app.errorhandler(PydanticValidationError)
    def _handle_pydantic_error(error: PydanticValidationError):
        wrapped = ValidationError("Invalid request payload")
        return jsonify(_to_payload(wrapped)), wrapped.status_code
