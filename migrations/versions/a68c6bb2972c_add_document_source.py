"""add_document_source

Revision ID: a68c6bb2972c
Revises: d63e9f7661dd
Create Date: 2023-07-26 22:56:57.273888

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a68c6bb2972c'
down_revision = 'd63e9f7661dd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('file', sa.Column('source', sa.String(), nullable=True))


def downgrade():
    op.drop_column('file', 'source')
