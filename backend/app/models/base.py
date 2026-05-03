"""Shared SQLAlchemy base utilities."""

from __future__ import annotations

from datetime import UTC, datetime
import uuid

from app.extensions import db


def generate_uuid() -> str:
    return str(uuid.uuid4())


class UUIDPrimaryKeyMixin:
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
