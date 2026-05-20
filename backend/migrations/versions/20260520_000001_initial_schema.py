"""initial schema baseline

Revision ID: 20260520_000001
Revises:
Create Date: 2026-05-20 12:00:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260520_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create integrity constraint(s) required by the current model set.

    Note: this repository currently creates tables in tests via SQLAlchemy metadata;
    production deploys must run Alembic migrations instead.
    """

    with op.batch_alter_table("daily_usage", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            "uq_daily_usage_user_feature_date",
            ["user_id", "feature_key", "usage_date"],
        )


def downgrade() -> None:
    with op.batch_alter_table("daily_usage", schema=None) as batch_op:
        batch_op.drop_constraint("uq_daily_usage_user_feature_date", type_="unique")
