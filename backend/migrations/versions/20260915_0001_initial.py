"""initial clean schema

Revision ID: 20260915_0001
Revises:
Create Date: 2026-09-15
"""
from datetime import UTC, datetime
from typing import Sequence
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260915_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

account_status = sa.Enum("ACTIVE", "SUSPENDED", name="account_status")
user_status = sa.Enum("ACTIVE", "SUSPENDED", name="user_status")
feature_key = sa.Enum("CORE", "PUBLICATIONS", "DOCUMENTS", "TEMPLATES", "FINANCE", "REPORTS", name="feature_key")
limit_kind = sa.Enum("USERS", "MONITORED_CASES", "STORAGE", name="limit_kind")


def upgrade() -> None:
    installation = op.create_table(
        "installation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.bulk_insert(installation, [{"id": uuid4(), "created_at": datetime.now(UTC)}])

    op.create_table(
        "plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("is_trial", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "plan_features",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_key", feature_key, nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("plan_id", "feature_key"),
    )
    op.create_table(
        "plan_limits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("limit_kind", limit_kind, nullable=False),
        sa.Column("value", sa.Integer(), nullable=True),
        sa.Column("pending", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("plan_id", "limit_kind"),
        sa.CheckConstraint("value IS NULL OR value >= 0", name="ck_plan_limit_non_negative"),
    )
    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("tax_id", sa.String(32), nullable=True),
        sa.Column("phone", sa.String(40), nullable=True),
        sa.Column("institutional_email", sa.String(320), nullable=True),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="America/Sao_Paulo"),
        sa.Column("logo_key", sa.Text(), nullable=True),
        sa.Column("status", account_status, nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plans.id"), nullable=False),
        sa.Column("trial_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("status", user_status, nullable=False),
        sa.Column("is_system_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("permissions", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("photo_key", sa.Text(), nullable=True),
        sa.Column("preferences", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_account_id", "users", ["account_id"])


def downgrade() -> None:
    op.drop_index("ix_users_account_id", table_name="users")
    op.drop_table("users")
    op.drop_table("accounts")
    op.drop_table("plan_limits")
    op.drop_table("plan_features")
    op.drop_table("plans")
    op.drop_table("installation")
    user_status.drop(op.get_bind(), checkfirst=True)
    account_status.drop(op.get_bind(), checkfirst=True)
    limit_kind.drop(op.get_bind(), checkfirst=True)
    feature_key.drop(op.get_bind(), checkfirst=True)
