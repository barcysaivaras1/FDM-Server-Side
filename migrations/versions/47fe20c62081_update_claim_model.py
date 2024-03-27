"""empty message

Revision ID: 47fe20c62081
Revises: 53fc912afc28
Create Date: 2024-03-26 13:59:16.020799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47fe20c62081'
down_revision = '53fc912afc28'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('claim', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('amount', sa.Float(), nullable=False))
        batch_op.drop_column('temp')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('claim', schema=None) as batch_op:
        batch_op.add_column(sa.Column('temp', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.drop_column('amount')
        batch_op.drop_column('title')

    # ### end Alembic commands ###