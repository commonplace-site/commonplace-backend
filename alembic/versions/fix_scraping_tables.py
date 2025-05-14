"""fix scraping tables

Revision ID: fix_scraping_tables
Revises: 180531b39479
Create Date: 2024-03-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import ProgrammingError

# revision identifiers, used by Alembic.
revision = 'fix_scraping_tables'
down_revision = '180531b39479'
branch_labels = None
depends_on = None

def upgrade():
    # Get database connection
    connection = op.get_bind()
    
    # Check if scraping_sources table exists
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'scraping_sources' not in tables:
        # Create scraping_sources table if it doesn't exist
        op.create_table(
            'scraping_sources',
            sa.Column('id', sa.BigInteger(), primary_key=True),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('source_url', sa.Text(), nullable=False),
            sa.Column('active', sa.Boolean(), default=True, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
    
    if 'scraped_contents' not in tables:
        # Create scraped_contents table if it doesn't exist
        op.create_table(
            'scraped_contents',
            sa.Column('id', sa.BigInteger(), primary_key=True),
            sa.Column('source_id', sa.BigInteger(), nullable=False, index=True),
            sa.Column('title', sa.String(255), nullable=True),
            sa.Column('summary', sa.Text(), nullable=True),
            sa.Column('full_text', sa.Text(), nullable=True),
            sa.Column('level_flag', sa.String(50), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['source_id'], ['scraping_sources.id'], name='fk_scraped_contents_source'),
            sa.PrimaryKeyConstraint('id')
        )

def downgrade():
    # Get database connection
    connection = op.get_bind()
    
    # Check if tables exist before dropping
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'scraped_contents' in tables:
        op.drop_table('scraped_contents')
    if 'scraping_sources' in tables:
        op.drop_table('scraping_sources') 