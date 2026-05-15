"""create scan verification tables

Revision ID: 20260515_0001
Revises:
Create Date: 2026-05-15 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260515_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_url", sa.String(length=500), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scans_domain"), "scans", ["domain"], unique=False)

    op.create_table(
        "verifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("method", sa.String(length=20), nullable=False),
        sa.Column("token", sa.String(length=100), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("verified_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_verifications_domain"),
        "verifications",
        ["domain"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_verifications_domain"), table_name="verifications")
    op.drop_table("verifications")
    op.drop_index(op.f("ix_scans_domain"), table_name="scans")
    op.drop_table("scans")
