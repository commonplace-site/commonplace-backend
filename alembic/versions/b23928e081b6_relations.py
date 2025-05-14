"""relations 

Revision ID: b23928e081b6
Revises: fe66c44c34e4
Create Date: 2025-05-13 14:26:31.170003

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b23928e081b6'
down_revision: Union[str, None] = 'fe66c44c34e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
