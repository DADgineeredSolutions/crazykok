"""add event research fields

Revision ID: 9a7f9e8b6d21
Revises: 52d7c0a57cb7
Create Date: 2026-07-03 01:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '9a7f9e8b6d21'
down_revision = '52d7c0a57cb7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('events', sa.Column('application_deadline', sa.Date(), nullable=True))
    op.add_column(
        'events',
        sa.Column(
            'application_status',
            sa.String(length=50),
            server_default='researching',
            nullable=False,
        ),
    )
    op.add_column('events', sa.Column('source_url', sa.String(length=500), nullable=True))
    op.add_column('events', sa.Column('notes', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('events', 'notes')
    op.drop_column('events', 'source_url')
    op.drop_column('events', 'application_status')
    op.drop_column('events', 'application_deadline')
