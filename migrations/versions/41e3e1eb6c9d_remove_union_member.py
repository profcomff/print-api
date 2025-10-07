"""remove union_member

Revision ID: 41e3e1eb6c9d
Revises: a68c6bb2972c
Create Date: 2025-10-07 19:40:11.770337

"""
from alembic import op
import sqlalchemy as sa


revision = '41e3e1eb6c9d'
down_revision = 'a68c6bb2972c'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('file_owner_id_fkey', 'file', type_='foreignkey')
    op.drop_constraint('print_fact_owner_id_fkey', 'print_fact', type_='foreignkey')
    op.drop_table('union_member')
    op.alter_column('file', 'source',
               existing_type=sa.VARCHAR(),
               nullable=False)


def downgrade():
    op.alter_column('file', 'source',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_table('union_member',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('surname', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('union_number', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('student_number', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='union_member_pkey')
    )
    op.create_foreign_key('file_owner_id_fkey', 'file', 'union_member', ['owner_id'], ['id'])
    op.create_foreign_key('print_fact_owner_id_fkey', 'print_fact', 'union_member', ['owner_id'], ['id'])
