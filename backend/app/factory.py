import os
from flask import Flask
from app.api.route_registry import register_routes
from app.config import DevelopmentConfig, ProductionConfig, TestingConfig
from app.extensions import cors, db, limiter, migrate

CONFIG_MAP = {"development": DevelopmentConfig, "testing": TestingConfig, "production": ProductionConfig}

def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    selected = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(CONFIG_MAP.get(selected, DevelopmentConfig))
    db.init_app(app); migrate.init_app(app, db); cors.init_app(app); limiter.init_app(app)
    register_routes(app)
    return app
