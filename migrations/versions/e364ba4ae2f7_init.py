"""Init

Revision ID: e364ba4ae2f7
Revises:
Create Date: 2021-11-02 18:34:31.049423

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'e364ba4ae2f7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'union_member',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('surname', sa.String(), nullable=False),
        sa.Column('number', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'file',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pin', sa.String(), nullable=False),
        sa.Column('file', sa.String(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['owner_id'],
            ['union_member.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('file')
    op.drop_table('union_member')
