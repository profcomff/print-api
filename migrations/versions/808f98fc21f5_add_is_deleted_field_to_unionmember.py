"""Add is_deleted field to UnionMember

Revision ID: 808f98fc21f5
Revises: a68c6bb2972c
Create Date: 2024-11-07 21:35:48.483333

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '808f98fc21f5'
down_revision = 'a68c6bb2972c'
branch_labels = None
depends_on = None


def upgrade():

    op.alter_column('file', 'source', existing_type=sa.VARCHAR(), nullable=False)
    op.add_column('union_member', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    op.execute(f'UPDATE "union_member" SET  is_deleted = False')
    op.alter_column('union_member', 'is_deleted', nullable=False)


def downgrade():
    op.drop_column('union_member', 'is_deleted')
    op.alter_column('file', 'source', existing_type=sa.VARCHAR(), nullable=True)
