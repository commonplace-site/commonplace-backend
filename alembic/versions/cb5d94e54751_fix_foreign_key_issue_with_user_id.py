"""Fix foreign key issue with user_id

Revision ID: cb5d94e54751
Revises: 949ed1c495d8
Create Date: 2025-05-04 22:57:14.412255

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cb5d94e54751'
down_revision: Union[str, None] = '949ed1c495d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create UUID extension first
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
    
    # Drop foreign key constraint before dropping the column
    op.drop_constraint('files_user_id_fkey', 'files', type_='foreignkey')
    
    # Create a temporary column for UUID
    op.add_column('users', sa.Column('new_id', postgresql.UUID(), nullable=True))
    
    # Generate UUIDs for existing records
    op.execute("UPDATE users SET new_id = uuid_generate_v4()")
    
    # Make the new column not nullable
    op.alter_column('users', 'new_id', nullable=False)
    
    # Drop the old id column
    op.drop_column('users', 'id')
    
    # Rename new_id to id
    op.alter_column('users', 'new_id', new_column_name='id')
    
    # Set id as primary key
    op.create_primary_key('users_pkey', 'users', ['id'])
    
    # Drop the old user_id column from files
    op.drop_column('files', 'user_id')
    
    # Add new user_id column with UUID type
    op.add_column('files', sa.Column('user_id', postgresql.UUID(), nullable=False))
    
    # Recreate foreign key
    op.create_foreign_key('files_user_id_fkey', 'files', 'users', ['user_id'], ['id'])

def downgrade() -> None:
    # Drop foreign key constraint before dropping the column
    op.drop_constraint('files_user_id_fkey', 'files', type_='foreignkey')
    
    # Drop the UUID user_id column
    op.drop_column('files', 'user_id')
    
    # Add back the old user_id column as bigint
    op.add_column('files', sa.Column('user_id', sa.BigInteger(), nullable=False))
    
    # Create a temporary column for bigint
    op.add_column('users', sa.Column('old_id', sa.BigInteger(), nullable=True))
    
    # Generate sequential IDs for existing records
    op.execute(""" 
        WITH numbered_rows AS (
            SELECT id, ROW_NUMBER() OVER (ORDER BY id) as row_num
            FROM users
        )
        UPDATE users SET old_id = numbered_rows.row_num
        FROM numbered_rows
        WHERE users.id = numbered_rows.id
    """)
    
    # Make the new column not nullable
    op.alter_column('users', 'old_id', nullable=False)
    
    # Drop the UUID id column
    op.drop_column('users', 'id')
    
    # Rename old_id to id
    op.alter_column('users', 'old_id', new_column_name='id')
    
    # Set id as primary key
    op.create_primary_key('users_pkey', 'users', ['id'])
    
    # Recreate foreign key
    op.create_foreign_key('files_user_id_fkey', 'files', 'users', ['user_id'], ['id'])
    
    # Drop UUID extension
    op.execute("DROP EXTENSION IF EXISTS \"uuid-ossp\";")
