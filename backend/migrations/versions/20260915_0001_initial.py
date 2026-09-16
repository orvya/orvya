"""initial foundation

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


def upgrade() -> None:
    installation = op.create_table(
        "installation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.bulk_insert(
        installation,
        [{"id": uuid4(), "created_at": datetime.now(UTC)}],
    )


def downgrade() -> None:
    op.drop_table("installation")
