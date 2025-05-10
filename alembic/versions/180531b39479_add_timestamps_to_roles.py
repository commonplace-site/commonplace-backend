"""add_timestamps_to_roles

Revision ID: 180531b39479
Revises: dc74883351bf
Create Date: 2025-05-09 22:46:32.273561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TIMESTAMP


# revision identifiers, used by Alembic.
revision: str = '180531b39479'
down_revision: Union[str, None] = 'dc74883351bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('roles', sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('roles', sa.Column('updated_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('roles', 'updated_at')
    op.drop_column('roles', 'created_at')
