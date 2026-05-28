"""add vulnerabilities snippets grade

Revision ID: 20260528_0002
Revises: 20260515_0001
Create Date: 2026-05-28 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260528_0002"
down_revision: Union[str, None] = "20260515_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("scans", sa.Column("security_grade", sa.String(length=1), nullable=True))
    op.add_column("scans", sa.Column("total_score", sa.Numeric(4, 1), nullable=True))

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

    op.create_table(
        "vulnerabilities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(length=10), nullable=False),
        sa.Column("cvss_score", sa.Numeric(3, 1), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_vulnerabilities_scan_id"),
        "vulnerabilities",
        ["scan_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_vulnerabilities_type"),
        "vulnerabilities",
        ["type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_vulnerabilities_type"), table_name="vulnerabilities")
    op.drop_index(op.f("ix_vulnerabilities_scan_id"), table_name="vulnerabilities")
    op.drop_table("vulnerabilities")
    op.drop_index(op.f("ix_snippets_vuln_type"), table_name="snippets")
    op.drop_table("snippets")
    op.drop_column("scans", "total_score")
    op.drop_column("scans", "security_grade")
