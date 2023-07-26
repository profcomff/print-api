"""Print options

Revision ID: 44494b133481
Revises: e364ba4ae2f7
Create Date: 2021-11-10 19:26:16.570560

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '44494b133481'
down_revision = 'e364ba4ae2f7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('file', sa.Column('option_pages', sa.String(), nullable=True))
    op.add_column('file', sa.Column('option_copies', sa.Integer(), nullable=True))
    op.add_column('file', sa.Column('option_two_sided', sa.Boolean(), nullable=True))
    op.add_column('file', sa.Column('source', sa.String(), nullable=True))


def downgrade():
    op.drop_column('file', 'option_two_sided')
    op.drop_column('file', 'option_copies')
    op.drop_column('file', 'option_pages')
    op.drop_column('file', 'source')
