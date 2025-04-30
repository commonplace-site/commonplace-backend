"""updated user table

Revision ID: 408c8a638df3
Revises: ba70d460c5bf
Create Date: 2025-04-30 20:55:51.067747

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '408c8a638df3'
down_revision: Union[str, None] = 'ba70d460c5bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: Add the column as nullable
    op.add_column('users', sa.Column('first_Name', sa.String(length=256), nullable=True))
    op.add_column('users', sa.Column('last_Name', sa.String(length=256), nullable=True))

    # Step 2: Set default value for existing rows (optional, adjust as needed)
    op.execute("UPDATE users SET \"first_Name\" = 'Default' WHERE \"first_Name\" IS NULL")

    # Step 3: Alter the column to be NOT NULL
    op.alter_column('users', 'first_Name', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'last_Name')
    op.drop_column('users', 'first_Name')
