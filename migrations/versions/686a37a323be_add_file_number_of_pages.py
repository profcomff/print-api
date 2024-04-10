"""add_file_number_of_pages

Revision ID: 686a37a323be
Revises: 692fe4f50da7
Create Date: 2023-04-29 19:38:02.676614

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '686a37a323be'
down_revision = '692fe4f50da7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('file', sa.Column('number_of_pages', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('file', 'number_of_pages')
