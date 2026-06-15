"""add users schedules notifications

Revision ID: 20260614_0004
Revises: 20260528_0002
Create Date: 2026-06-14 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260614_0004"
down_revision: Union[str, None] = "20260528_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.add_column(
        "verifications",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_verifications_user_id_users",
        "verifications",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_verifications_user_id"),
        "verifications",
        ["user_id"],
        unique=False,
    )

    op.add_column(
        "scans",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_scans_user_id_users",
        "scans",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_scans_user_id"), "scans", ["user_id"], unique=False)

    op.create_table(
        "scan_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("frequency", sa.String(length=20), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=True),
        sa.Column("run_time", sa.Time(), nullable=False),
        sa.Column("timezone", sa.String(length=50), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("last_run_at", sa.DateTime(), nullable=True),
        sa.Column("next_run_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "frequency IN ('daily', 'weekly', 'monthly')",
            name="ck_scan_schedules_frequency",
        ),
        sa.CheckConstraint(
            "(frequency = 'daily' AND day_of_week IS NULL) OR "
            "(frequency = 'weekly' AND day_of_week BETWEEN 0 AND 6)",
            name="ck_scan_schedules_frequency_day",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "domain", name="uq_scan_schedules_user_domain"),
    )
    op.create_index(
        op.f("ix_scan_schedules_user_id"),
        "scan_schedules",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_scan_schedules_domain"),
        "scan_schedules",
        ["domain"],
        unique=False,
    )
    op.create_index(
        op.f("ix_scan_schedules_next_run_at"),
        "scan_schedules",
        ["next_run_at"],
        unique=False,
    )

    op.create_table(
        "notification_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email_enabled", sa.Boolean(), nullable=False),
        sa.Column("email_address", sa.String(length=255), nullable=True),
        sa.Column("slack_enabled", sa.Boolean(), nullable=False),
        sa.Column("slack_webhook_url", sa.Text(), nullable=True),
        sa.Column("kakaowork_enabled", sa.Boolean(), nullable=False),
        sa.Column("kakaowork_webhook_url", sa.Text(), nullable=True),
        sa.Column("notify_new_vulnerability", sa.Boolean(), nullable=False),
        sa.Column("notify_score_drop", sa.Boolean(), nullable=False),
        sa.Column("notify_certificate_expiry", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_notification_settings_user_id"),
        "notification_settings",
        ["user_id"],
        unique=True,
    )

    op.create_table(
        "notification_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("setting_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("recipient", sa.String(length=500), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("detail", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "channel IN ('email', 'slack', 'kakaowork')",
            name="ck_notification_logs_channel",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'sent', 'failed')",
            name="ck_notification_logs_status",
        ),
        sa.CheckConstraint(
            "event_type IN "
            "('new_vulnerability', 'score_drop', 'certificate_expiry', 'scan_failed')",
            name="ck_notification_logs_event_type",
        ),
        sa.ForeignKeyConstraint(
            ["setting_id"],
            ["notification_settings.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_notification_logs_user_id"),
        "notification_logs",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_logs_scan_id"),
        "notification_logs",
        ["scan_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_logs_event_type"),
        "notification_logs",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_logs_status"),
        "notification_logs",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_notification_logs_status"), table_name="notification_logs")
    op.drop_index(op.f("ix_notification_logs_event_type"), table_name="notification_logs")
    op.drop_index(op.f("ix_notification_logs_scan_id"), table_name="notification_logs")
    op.drop_index(op.f("ix_notification_logs_user_id"), table_name="notification_logs")
    op.drop_table("notification_logs")

    op.drop_index(
        op.f("ix_notification_settings_user_id"),
        table_name="notification_settings",
    )
    op.drop_table("notification_settings")

    op.drop_index(op.f("ix_scan_schedules_next_run_at"), table_name="scan_schedules")
    op.drop_index(op.f("ix_scan_schedules_domain"), table_name="scan_schedules")
    op.drop_index(op.f("ix_scan_schedules_user_id"), table_name="scan_schedules")
    op.drop_table("scan_schedules")

    op.drop_index(op.f("ix_scans_user_id"), table_name="scans")
    op.drop_constraint("fk_scans_user_id_users", "scans", type_="foreignkey")
    op.drop_column("scans", "user_id")

    op.drop_index(op.f("ix_verifications_user_id"), table_name="verifications")
    op.drop_constraint(
        "fk_verifications_user_id_users",
        "verifications",
        type_="foreignkey",
    )
    op.drop_column("verifications", "user_id")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
