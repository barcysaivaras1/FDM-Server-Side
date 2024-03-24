"""Add status column to Claim model

Revision ID: 07f33b49fa31
Revises: d20d7edeb2b0
Create Date: 2024-03-24 14:13:08.443107

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '07f33b49fa31'
down_revision = 'd20d7edeb2b0'
branch_labels = None
depends_on = None


def upgrade():
    sa.Enum('PENDING', 'APPROVED', 'DENIED', name='claim_status').create(op.get_bind())
    op.add_column('claim',
    sa.Column('status', postgresql.ENUM('PENDING', 'APPROVED', 'DENIED', name='claim_status', create_type=False))
    )


def downgrade():
    pass
