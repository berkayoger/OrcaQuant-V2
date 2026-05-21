import os

from flask import Flask

from app.api.route_registry import register_routes
from app.cli import register_cli
from app.config import DevelopmentConfig, ProductionConfig, TestingConfig
from app.core.errors.handlers import register_error_handlers
from app.core.observability.request_context import register_request_id_middleware
from app.core.security.cors_policy import resolve_cors_origins
from app.core.security.runtime_config import validate_runtime_config
from app.core.security.security_headers import apply_security_headers
from app.extensions import cors, db, limiter, migrate
import app.models  # noqa: F401

CONFIG_MAP = {"development": DevelopmentConfig, "testing": TestingConfig, "production": ProductionConfig}


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    selected = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(CONFIG_MAP.get(selected, DevelopmentConfig))
    validate_runtime_config(app, selected)

    if selected == "production":
        if not os.getenv("SECRET_KEY"):
            raise RuntimeError("SECRET_KEY must be set in production")
        if not os.getenv("CORS_ALLOWED_ORIGINS"):
            raise RuntimeError("CORS_ALLOWED_ORIGINS must be explicitly set in production")

    db.init_app(app)
    migrate.init_app(app, db)
    cors_origins = resolve_cors_origins(app, selected)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": cors_origins}},
        supports_credentials=True,
        vary_header=True,
    )
    limiter.init_app(app)

    register_request_id_middleware(app)
    register_error_handlers(app)
    apply_security_headers(app)
    register_routes(app)
    register_cli(app)
    return app
