"""Your message

Revision ID: fe66c44c34e4
Revises: fix_scraping_tables
Create Date: 2025-05-13 14:26:20.947783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe66c44c34e4'
down_revision: Union[str, None] = 'fix_scraping_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
