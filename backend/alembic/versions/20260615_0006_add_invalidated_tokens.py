"""add invalidated tokens

Revision ID: 20260615_0006
Revises: 20260615_0005
Create Date: 2026-06-15 18:58:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260615_0006'
down_revision = '20260615_0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'invalidated_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(length=512), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invalidated_tokens_token'), 'invalidated_tokens', ['token'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_invalidated_tokens_token'), table_name='invalidated_tokens')
    op.drop_table('invalidated_tokens')
