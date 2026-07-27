"""Add soft delete

Revision ID: b617b731841e
Revises: 0001
Create Date: 2026-07-27 14:37:44.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b617b731841e'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('links', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.create_index(op.f('ix_links_is_deleted'), 'links', ['is_deleted'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_links_is_deleted'), table_name='links')
    op.drop_column('links', 'is_deleted')
