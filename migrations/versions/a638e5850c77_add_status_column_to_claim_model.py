"""Add status column to Claim model

Revision ID: a638e5850c77
Revises: d20d7edeb2b0
Create Date: 2024-03-23 17:11:43.782127

"""
from alembic import op
import sqlalchemy as sa

from app.models.claim import ClaimStatus

# revision identifiers, used by Alembic.
revision = 'a638e5850c77'
down_revision = 'd20d7edeb2b0'
branch_labels = None
depends_on = None


def upgrade():
    def upgrade():
        op.add_column('claim',
        sa.Column('status', sa.Enum(ClaimStatus))
    )

def downgrade():
    pass
