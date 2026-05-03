from flask import Flask
from app.api.v1.health_routes import health_bp

def register_routes(app: Flask) -> None:
    app.register_blueprint(health_bp, url_prefix="/api/v1")
