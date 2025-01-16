"""Add is_deleted field to UnionMember

Revision ID: c29b6ffbfed4
Revises: a68c6bb2972c
Create Date: 2024-11-22 17:50:35.569723

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'c29b6ffbfed4'
down_revision = 'a68c6bb2972c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'union_member', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false())
    )


def downgrade():
    op.drop_column('union_member', 'is_deleted')
    op.alter_column('file', 'source', existing_type=sa.VARCHAR(), nullable=True)
