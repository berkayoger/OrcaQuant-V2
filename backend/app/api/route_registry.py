from flask import Flask

from app.api.v1.admin.admin_audit_routes import admin_audit_bp
from app.api.v1.admin.admin_dashboard_routes import admin_dashboard_bp
from app.api.v1.admin.admin_engine_routes import admin_engine_bp
from app.api.v1.admin.admin_feature_flag_routes import admin_feature_flag_bp
from app.api.v1.admin.admin_limit_routes import admin_limit_bp
from app.api.v1.admin.admin_payment_routes import admin_payment_bp
from app.api.v1.admin.admin_plan_routes import admin_plan_bp
from app.api.v1.admin.admin_security_routes import admin_security_bp
from app.api.v1.admin.admin_system_routes import admin_system_bp
from app.api.v1.admin.admin_user_routes import admin_user_bp
from app.api.v1.alert_routes import alert_bp
from app.api.v1.analysis_routes import analysis_bp
from app.api.v1.asset_routes import asset_bp
from app.api.v1.auth_routes import auth_bp
from app.api.v1.billing_routes import billing_bp
from app.api.v1.dashboard_routes import dashboard_bp
from app.api.v1.docs_routes import docs_bp
from app.api.v1.health_routes import health_bp
from app.api.v1.history_routes import history_bp
from app.api.v1.market_routes import market_bp
from app.api.v1.portfolio_routes import portfolio_bp
from app.api.v1.profile_routes import profile_bp
from app.api.v1.scenario_routes import scenario_bp
from app.api.v1.settings_routes import settings_bp
from app.api.v1.user_routes import user_bp
from app.api.v1.watchlist_routes import watchlist_bp
from app.api.v1.webhook_routes import webhook_bp


def register_routes(app: Flask) -> None:
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(user_bp, url_prefix="/api/v1/me")
    app.register_blueprint(profile_bp, url_prefix="/api/v1/profile")
    app.register_blueprint(asset_bp, url_prefix="/api/v1/assets")
    app.register_blueprint(market_bp, url_prefix="/api/v1/market")
    app.register_blueprint(analysis_bp, url_prefix="/api/v1/analysis")
    app.register_blueprint(scenario_bp, url_prefix="/api/v1/scenario")
    app.register_blueprint(portfolio_bp, url_prefix="/api/v1/portfolio")
    app.register_blueprint(alert_bp, url_prefix="/api/v1/alerts")
    app.register_blueprint(watchlist_bp, url_prefix="/api/v1/watchlist")
    app.register_blueprint(history_bp, url_prefix="/api/v1/history")
    app.register_blueprint(billing_bp, url_prefix="/api/v1/billing")
    app.register_blueprint(settings_bp, url_prefix="/api/v1/settings")
    app.register_blueprint(webhook_bp, url_prefix="/api/v1/webhooks")
    app.register_blueprint(dashboard_bp, url_prefix="/api/v1/dashboard")
    app.register_blueprint(docs_bp, url_prefix="/api/v1/docs")

    app.register_blueprint(admin_dashboard_bp, url_prefix="/api/v1/admin/dashboard")
    app.register_blueprint(admin_user_bp, url_prefix="/api/v1/admin/users")
    app.register_blueprint(admin_plan_bp, url_prefix="/api/v1/admin/plans")
    app.register_blueprint(admin_limit_bp, url_prefix="/api/v1/admin/limits")
    app.register_blueprint(admin_feature_flag_bp, url_prefix="/api/v1/admin/feature-flags")
    app.register_blueprint(admin_payment_bp, url_prefix="/api/v1/admin/payments")
    app.register_blueprint(admin_engine_bp, url_prefix="/api/v1/admin/engines")
    app.register_blueprint(admin_audit_bp, url_prefix="/api/v1/admin/audit-logs")
    app.register_blueprint(admin_security_bp, url_prefix="/api/v1/admin/security")
    app.register_blueprint(admin_system_bp, url_prefix="/api/v1/admin/system")
