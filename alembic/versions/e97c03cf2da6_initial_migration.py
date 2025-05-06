"""Initial migration

Revision ID: e97c03cf2da6
Revises: 
Create Date: 2025-05-05 15:27:07.489485
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON, TIMESTAMP


# revision identifiers, used by Alembic.
revision: str = 'e97c03cf2da6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create roles table first since users reference it
    op.create_table('roles',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create users table
    op.create_table('users',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('first_Name', sa.String(256), nullable=False),
        sa.Column('last_Name', sa.String(256), nullable=True),
        sa.Column('email', sa.String(150), unique=True, nullable=False),
        sa.Column('password', sa.String(256), nullable=False),
        sa.Column('role_id', sa.BigInteger(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create profiles table
    op.create_table('profiles',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('user_id', UUID(), nullable=True),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('native_language', sa.String(50), nullable=True),
        sa.Column('target_language', sa.String(50), nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create files table
    op.create_table('files',
        sa.Column('id', UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()'), index=True),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('s3_url', sa.String(), nullable=False),
        sa.Column('uploaded_by', sa.String(), nullable=False),
        sa.Column('folder', sa.String(), nullable=False),
        sa.Column('filetype', sa.String(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', UUID(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create audio_files table
    op.create_table('audio_files',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', UUID(), nullable=True),
        sa.Column('audio_type', sa.String(50), nullable=True),
        sa.Column('file_url', sa.Text(), nullable=False),
        sa.Column('transcription_text', sa.Text(), nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create comprehension_logs table
    op.create_table('comprehension_logs',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', UUID(), nullable=True),
        sa.Column('material', sa.Text(), nullable=True),
        sa.Column('comprehension_score', sa.Integer(), nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create feedback_logs table
    op.create_table('feedback_logs',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', UUID(), nullable=True),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('related_module', sa.String(100), nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create grammar_logs table
    op.create_table('grammar_logs',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', UUID(), nullable=True),
        sa.Column('sentence', sa.Text(), nullable=False),
        sa.Column('grammar_issue', sa.Text(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create pronunciation_logs table
    op.create_table('pronunciation_logs',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', UUID(), nullable=True),
        sa.Column('original_text', sa.Text(), nullable=True),
        sa.Column('audio_file_url', sa.Text(), nullable=True),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create roleplay_sessions table
    op.create_table('roleplay_sessions',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', UUID(), nullable=True),
        sa.Column('scenario', sa.String(255), nullable=True),
        sa.Column('avatar_used', sa.String(100), nullable=True),
        sa.Column('recording_url', sa.Text(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create vocabulary_logs table
    op.create_table('vocabulary_logs',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', UUID(), nullable=True),
        sa.Column('word', sa.String(100), nullable=False),
        sa.Column('meaning', sa.String(255), nullable=True),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('added_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create lessons table
    op.create_table('lessons',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content_url', sa.Text(), nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create learning_modules table
    op.create_table('learning_modules',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), default='pending', nullable=True),
        sa.Column('active_user', sa.Integer(), default=0, nullable=True),
        sa.Column('last_updated_at', TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create integrations table
    op.create_table('integrations',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(50), nullable=True),
        sa.Column('status', sa.Boolean(), default=True, nullable=True),
        sa.Column('usage_count', sa.BigInteger(), default=0, nullable=True),
        sa.Column('usage_limit', sa.BigInteger(), nullable=True),
        sa.Column('base_url', sa.Text(), nullable=True),
        sa.Column('api_key', sa.Text(), nullable=True),
        sa.Column('config', JSON(), nullable=True),
        sa.Column('last_check_at', TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create diagnostic_results table
    op.create_table('diagnostic_results',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('student_id', sa.String(), index=True, nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('level', sa.String(), nullable=True),
        sa.Column('learning_content', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create scraping_sources table
    op.create_table('scraping_sources',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=False),
        sa.Column('active', sa.Boolean(), default=True, nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create scraped_contents table
    op.create_table('scraped_contents',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('source_id', sa.BigInteger(), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('full_text', sa.Text(), nullable=True),
        sa.Column('level_flag', sa.String(50), nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['scraping_sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop all tables in reverse order (respecting foreign key constraints)
    op.drop_table('scraped_contents')
    op.drop_table('scraping_sources')
    op.drop_table('diagnostic_results')
    op.drop_table('integrations')
    op.drop_table('learning_modules')
    op.drop_table('lessons')
    op.drop_table('vocabulary_logs')
    op.drop_table('roleplay_sessions')
    op.drop_table('pronunciation_logs')
    op.drop_table('grammar_logs')
    op.drop_table('feedback_logs')
    op.drop_table('comprehension_logs')
    op.drop_table('audio_files')
    op.drop_table('files')
    op.drop_table('profiles')
    op.drop_table('users')
    op.drop_table('roles')