"""soft-deletes

Revision ID: a9c4bf6370de
Revises: a68c6bb2972c
Create Date: 2025-10-11 01:33:01.717991

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a9c4bf6370de'
down_revision = 'a68c6bb2972c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('file', sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False))
    op.alter_column('file', 'option_pages', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column('file', 'option_copies', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('file', 'option_two_sided', existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column('file', 'number_of_pages', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('file', 'source', existing_type=sa.VARCHAR(), nullable=False)
    op.add_column(
        'print_fact', sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False)
    )
    op.alter_column('print_fact', 'sheets_used', existing_type=sa.INTEGER(), nullable=False)
    op.add_column(
        'union_member', sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False)
    )


def downgrade():
    op.drop_column('union_member', 'is_deleted')
    op.alter_column('print_fact', 'sheets_used', existing_type=sa.INTEGER(), nullable=True)
    op.drop_column('print_fact', 'is_deleted')
    op.alter_column('file', 'source', existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column('file', 'number_of_pages', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('file', 'option_two_sided', existing_type=sa.BOOLEAN(), nullable=True)
    op.alter_column('file', 'option_copies', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('file', 'option_pages', existing_type=sa.VARCHAR(), nullable=True)
    op.drop_column('file', 'is_deleted')
