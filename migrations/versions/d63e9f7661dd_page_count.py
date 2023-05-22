"""page_count

Revision ID: d63e9f7661dd
Revises: f6fb6304fb74
Create Date: 2023-05-15 18:38:40.964981

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'd63e9f7661dd'
down_revision = 'f6fb6304fb74'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('print_fact', sa.Column('sheets_used', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('print_fact', 'sheets_used')
