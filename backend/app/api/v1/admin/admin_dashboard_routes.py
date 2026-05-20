from flask import Blueprint

from app.common.responses import ok
from app.core.security.auth_guard import require_auth
from app.core.security.permission_guard import require_role
from app.models.payment import PaymentTransaction
from app.models.plan import Plan
from app.models.usage import FeatureLimit
from app.models.user import User


admin_dashboard_bp = Blueprint("admin_dashboard", __name__)


@admin_dashboard_bp.get("/")
@require_auth
@require_role("admin")
def get_admin_dashboard_summary():
    return ok(
        {
            "users": User.query.count(),
            "plans": Plan.query.count(),
            "active_plans": Plan.query.filter_by(is_active=True).count(),
            "feature_limits": FeatureLimit.query.count(),
            "payment_transactions": PaymentTransaction.query.count(),
        }
    )
