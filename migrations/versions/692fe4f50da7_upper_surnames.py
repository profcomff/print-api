"""Upper surnames

Revision ID: 692fe4f50da7
Revises: 09929802c3e1
Create Date: 2022-11-19 16:28:09.570088

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '692fe4f50da7'
down_revision = '09929802c3e1'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE union_member SET surname=UPPER(surname);")


def downgrade():
    pass
