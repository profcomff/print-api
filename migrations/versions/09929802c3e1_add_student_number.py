"""add student number

Revision ID: 09929802c3e1
Revises: 44494b133481
Create Date: 2022-09-02 21:29:38.712544

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '09929802c3e1'
down_revision = '44494b133481'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('union_member', sa.Column('student_number', sa.String(), nullable=True))
    op.alter_column('union_member', 'number', new_column_name='union_number', nullable=True)


def downgrade():
    op.execute("DELETE FROM union_member WHERE union_number IS NULL or union_number = '';")
    op.drop_column('union_member', 'student_number')
    op.alter_column('union_member', 'union_number', new_column_name='number', nullable=False)
