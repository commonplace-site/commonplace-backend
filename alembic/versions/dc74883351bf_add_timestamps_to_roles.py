"""add_timestamps_to_roles

Revision ID: dc74883351bf
Revises: e97c03cf2da6
Create Date: 2025-05-09 22:42:08.683085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc74883351bf'
down_revision: Union[str, None] = 'e97c03cf2da6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
