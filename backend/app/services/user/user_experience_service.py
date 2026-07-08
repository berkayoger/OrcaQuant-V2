from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.extensions import db
from app.models.alert_rule import AlertRule
from app.models.notification import Notification
from app.models.plan import Plan
from app.models.session import Session
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.watchlist import Watchlist

DEFAULT_NOTIFICATION_PREFERENCES = {
    "in_app": True,
    "daily_brief": True,
    "price_alerts": True,
    "risk_alerts": True,
    "product_updates": False,
    "email": False,
    "telegram": False,
    "push": False,
}

DEFAULT_ONBOARDING = {
    "profile_completed": False,
    "risk_profile_set": False,
    "watchlist_created": False,
    "first_alert_created": False,
    "daily_brief_enabled": True,
}

DEFAULT_PRIVACY = {
    "analytics_opt_in": False,
    "marketing_opt_in": False,
    "public_profile": False,
}

ALLOWED_RISK_PROFILES = {"CONSERVATIVE", "BALANCED", "AGGRESSIVE"}
ALLOWED_THEMES = {"light", "dark", "system"}
ALLOWED_CURRENCIES = {"TRY", "USD", "EUR", "USDT"}


class UserExperienceService:
    def get_or_create_profile(self, user_id: str) -> UserProfile:
        profile = UserProfile.query.filter_by(user_id=user_id).one_or_none()
        if profile:
            changed = False
            if not profile.notification_preferences:
                profile.notification_preferences = dict(DEFAULT_NOTIFICATION_PREFERENCES)
                changed = True
            if not profile.onboarding:
                profile.onboarding = dict(DEFAULT_ONBOARDING)
                changed = True
            if not profile.privacy:
                profile.privacy = dict(DEFAULT_PRIVACY)
                changed = True
            if changed:
                db.session.commit()
            return profile
        profile = UserProfile(
            user_id=user_id,
            notification_preferences=dict(DEFAULT_NOTIFICATION_PREFERENCES),
            onboarding=dict(DEFAULT_ONBOARDING),
            privacy=dict(DEFAULT_PRIVACY),
        )
        db.session.add(profile)
        db.session.commit()
        return profile

    def profile_payload(self, user: User) -> dict:
        profile = self.get_or_create_profile(user.id)
        return {
            "user_id": user.id,
            "email": user.email,
            "username": user.username,
            "display_name": profile.display_name,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "risk_profile": profile.risk_profile,
            "preferred_horizon_days": profile.preferred_horizon_days,
            "max_drawdown_tolerance": profile.max_drawdown_tolerance,
            "capital": self._decimal_to_float(profile.capital),
            "preferred_currency": profile.preferred_currency,
            "locale": profile.locale,
            "timezone": profile.timezone,
            "theme": profile.theme,
            "notification_preferences": self._merged_notifications(profile.notification_preferences),
            "onboarding": self.onboarding_status(user),
            "privacy": {**DEFAULT_PRIVACY, **(profile.privacy or {})},
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
        }

    def update_profile(self, user: User, payload: dict[str, Any]) -> dict:
        profile = self.get_or_create_profile(user.id)
        if "display_name" in payload:
            profile.display_name = self._optional_string(payload.get("display_name"), 120)
        if "bio" in payload:
            profile.bio = self._optional_string(payload.get("bio"), 280)
        if "avatar_url" in payload:
            profile.avatar_url = self._optional_string(payload.get("avatar_url"), 512)
        if "risk_profile" in payload:
            risk_profile = str(payload.get("risk_profile") or "").strip().upper()
            if risk_profile not in ALLOWED_RISK_PROFILES:
                raise ValueError(f"risk_profile must be one of {sorted(ALLOWED_RISK_PROFILES)}")
            profile.risk_profile = risk_profile
        if "preferred_horizon_days" in payload:
            profile.preferred_horizon_days = self._bounded_int(payload.get("preferred_horizon_days"), 1, 3650)
        if "max_drawdown_tolerance" in payload:
            profile.max_drawdown_tolerance = self._bounded_float(payload.get("max_drawdown_tolerance"), 0.0, 1.0)
        if "capital" in payload:
            profile.capital = self._optional_decimal(payload.get("capital"))
        profile.onboarding = self.onboarding_status(user)
        db.session.commit()
        return self.profile_payload(user)

    def settings_payload(self, user: User) -> dict:
        profile = self.get_or_create_profile(user.id)
        return {
            "locale": profile.locale,
            "timezone": profile.timezone,
            "theme": profile.theme,
            "preferred_currency": profile.preferred_currency,
            "notification_preferences": self._merged_notifications(profile.notification_preferences),
            "privacy": {**DEFAULT_PRIVACY, **(profile.privacy or {})},
        }

    def update_settings(self, user: User, payload: dict[str, Any]) -> dict:
        profile = self.get_or_create_profile(user.id)
        if "locale" in payload:
            profile.locale = self._required_string(payload.get("locale"), 16)
        if "timezone" in payload:
            profile.timezone = self._required_string(payload.get("timezone"), 64)
        if "theme" in payload:
            theme = str(payload.get("theme") or "").strip().lower()
            if theme not in ALLOWED_THEMES:
                raise ValueError(f"theme must be one of {sorted(ALLOWED_THEMES)}")
            profile.theme = theme
        if "preferred_currency" in payload:
            currency = str(payload.get("preferred_currency") or "").strip().upper()
            if currency not in ALLOWED_CURRENCIES:
                raise ValueError(f"preferred_currency must be one of {sorted(ALLOWED_CURRENCIES)}")
            profile.preferred_currency = currency
        if "notification_preferences" in payload:
            profile.notification_preferences = self._update_boolean_map(
                base=self._merged_notifications(profile.notification_preferences),
                updates=payload.get("notification_preferences"),
            )
        if "privacy" in payload:
            profile.privacy = self._update_boolean_map(base={**DEFAULT_PRIVACY, **(profile.privacy or {})}, updates=payload.get("privacy"))
        db.session.commit()
        return self.settings_payload(user)

    def update_notification_preferences(self, user: User, payload: dict[str, Any]) -> dict:
        profile = self.get_or_create_profile(user.id)
        profile.notification_preferences = self._update_boolean_map(self._merged_notifications(profile.notification_preferences), payload)
        db.session.commit()
        return self._merged_notifications(profile.notification_preferences)

    def onboarding_status(self, user: User) -> dict:
        profile = self.get_or_create_profile(user.id) if not isinstance(user, UserProfile) else user
        watchlist_symbols = self._watchlist_symbols(user.id) if isinstance(user, User) else []
        alert_count = AlertRule.query.filter_by(user_id=user.id).count() if isinstance(user, User) else 0
        computed = {
            "profile_completed": bool(getattr(profile, "display_name", None) and getattr(profile, "risk_profile", None)),
            "risk_profile_set": bool(getattr(profile, "risk_profile", None)),
            "watchlist_created": bool(watchlist_symbols),
            "first_alert_created": alert_count > 0,
            "daily_brief_enabled": self._merged_notifications(getattr(profile, "notification_preferences", {}) or {}).get("daily_brief", True),
        }
        return {**DEFAULT_ONBOARDING, **(getattr(profile, "onboarding", {}) or {}), **computed}

    def home_payload(self, user: User) -> dict:
        profile = self.get_or_create_profile(user.id)
        plan = Plan.query.filter_by(id=user.plan_id).one_or_none() if user.plan_id else None
        unread = Notification.query.filter_by(user_id=user.id, status="unread").count()
        alert_count = AlertRule.query.filter_by(user_id=user.id).count()
        active_alerts = [row for row in AlertRule.query.filter_by(user_id=user.id).all() if (row.data or {}).get("enabled", True)]
        watchlist_symbols = self._watchlist_symbols(user.id)
        onboarding = self.onboarding_status(user)
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "display_name": profile.display_name,
                "is_email_verified": user.is_email_verified,
                "role": user.role,
                "plan_code": plan.code if plan else None,
                "subscription_status": user.subscription_status,
            },
            "profile": self.profile_payload(user),
            "summary": {
                "watchlist_count": len(watchlist_symbols),
                "alert_count": alert_count,
                "active_alert_count": len(active_alerts),
                "unread_notification_count": unread,
                "profile_completion_percent": self._completion_percent(onboarding),
            },
            "watchlist_symbols": watchlist_symbols,
            "onboarding": onboarding,
            "quick_actions": self._quick_actions(user, onboarding, watchlist_symbols, alert_count),
        }

    def export_payload(self, user: User) -> dict:
        profile = self.profile_payload(user)
        watchlist = self._watchlist_symbols(user.id)
        alerts = [row.data or {} for row in AlertRule.query.filter_by(user_id=user.id).order_by(AlertRule.created_at.desc()).all()]
        notifications = [
            {
                "type": row.type,
                "status": row.status,
                "title": row.title,
                "body": row.body,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(500).all()
        ]
        sessions = [self._serialize_session(row) for row in Session.query.filter_by(user_id=user.id).order_by(Session.created_at.desc()).all()]
        return {
            "account": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "is_email_verified": user.is_email_verified,
                "subscription_status": user.subscription_status,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            },
            "profile": profile,
            "watchlist_symbols": watchlist,
            "alert_rules": alerts,
            "notifications": notifications,
            "sessions": sessions,
        }

    def list_sessions(self, user_id: str) -> list[dict]:
        return [self._serialize_session(row) for row in Session.query.filter_by(user_id=user_id).order_by(Session.created_at.desc()).all()]

    @staticmethod
    def _watchlist_symbols(user_id: str) -> list[str]:
        row = Watchlist.query.filter_by(user_id=user_id).order_by(Watchlist.created_at.asc()).first()
        return (row.data or {}).get("symbols") or [] if row else []

    @staticmethod
    def _merged_notifications(raw: dict | None) -> dict:
        return {**DEFAULT_NOTIFICATION_PREFERENCES, **(raw or {})}

    @staticmethod
    def _completion_percent(onboarding: dict) -> int:
        values = [bool(value) for value in onboarding.values()]
        return int(round(sum(values) / max(len(values), 1) * 100))

    @staticmethod
    def _quick_actions(user: User, onboarding: dict, watchlist_symbols: list[str], alert_count: int) -> list[dict]:
        actions = []
        if not user.is_email_verified:
            actions.append({"key": "verify_email", "label": "E-posta adresini doğrula", "href": "/settings/security"})
        if not onboarding.get("profile_completed"):
            actions.append({"key": "complete_profile", "label": "Risk profilini tamamla", "href": "/profile"})
        if not watchlist_symbols:
            actions.append({"key": "add_watchlist", "label": "İlk takip listenizi oluşturun", "href": "/watchlist"})
        if alert_count == 0:
            actions.append({"key": "create_alert", "label": "İlk alarm kuralını kur", "href": "/alerts"})
        if not actions:
            actions.append({"key": "open_dashboard", "label": "Market Cockpit'i aç", "href": "/dashboard"})
        return actions[:5]

    @staticmethod
    def _serialize_session(row: Session) -> dict:
        return {
            "id": row.id,
            "user_agent": row.user_agent,
            "ip_address": row.ip_address,
            "is_active": row.is_active,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            "revoked_at": row.revoked_at.isoformat() if row.revoked_at else None,
            "expires_at": row.expires_at.isoformat() if row.expires_at else None,
        }

    @staticmethod
    def _optional_string(value: Any, max_length: int) -> str | None:
        if value is None:
            return None
        clean = str(value).strip()
        return clean[:max_length] or None

    @staticmethod
    def _required_string(value: Any, max_length: int) -> str:
        clean = str(value or "").strip()
        if not clean:
            raise ValueError("value is required")
        return clean[:max_length]

    @staticmethod
    def _bounded_int(value: Any, minimum: int, maximum: int) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("value must be an integer") from exc
        if parsed < minimum or parsed > maximum:
            raise ValueError(f"value must be between {minimum} and {maximum}")
        return parsed

    @staticmethod
    def _bounded_float(value: Any, minimum: float, maximum: float) -> float:
        try:
            parsed = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("value must be numeric") from exc
        if parsed < minimum or parsed > maximum:
            raise ValueError(f"value must be between {minimum} and {maximum}")
        return parsed

    @staticmethod
    def _optional_decimal(value: Any) -> Decimal | None:
        if value in {None, ""}:
            return None
        try:
            parsed = Decimal(str(value))
        except Exception as exc:  # pragma: no cover - Decimal can raise multiple invalid-operation variants
            raise ValueError("capital must be numeric") from exc
        if parsed < 0:
            raise ValueError("capital cannot be negative")
        return parsed

    @staticmethod
    def _decimal_to_float(value: Decimal | None) -> float | None:
        return float(value) if value is not None else None

    @staticmethod
    def _update_boolean_map(base: dict, updates: Any) -> dict:
        if not isinstance(updates, dict):
            raise ValueError("updates must be an object")
        merged = dict(base)
        for key, value in updates.items():
            if key in merged:
                merged[key] = bool(value)
        return merged
