"""add_print_fact

Revision ID: f6fb6304fb74
Revises: 686a37a323be
Create Date: 2023-04-29 21:36:34.034457

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'f6fb6304fb74'
down_revision = '686a37a323be'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'print_fact',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['file_id'],
            ['file.id'],
        ),
        sa.ForeignKeyConstraint(
            ['owner_id'],
            ['union_member.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('print_fact')
