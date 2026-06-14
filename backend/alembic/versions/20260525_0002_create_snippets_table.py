"""create snippets table

Revision ID: 20260525_0002
Revises: 20260515_0001
Create Date: 2026-05-25 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260525_0002"
down_revision: Union[str, None] = "20260515_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "snippets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vuln_type", sa.String(length=50), nullable=False),
        sa.Column("server_type", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vuln_type", "server_type", name="uq_snippets_vuln_server"),
    )
    op.create_index(op.f("ix_snippets_vuln_type"), "snippets", ["vuln_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_snippets_vuln_type"), table_name="snippets")
    op.drop_table("snippets")
