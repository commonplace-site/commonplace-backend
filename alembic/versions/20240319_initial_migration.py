"""initial migration

Revision ID: 20240319_initial
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '20240319_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create uuid-ossp extension first
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Get connection and inspector
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()
    
    # Create businesses table if it doesn't exist
    if 'businesses' not in existing_tables:
        op.create_table('businesses',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('settings', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create users table if it doesn't exist
    if 'users' not in existing_tables:
        op.create_table('users',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('first_Name', sa.String(length=256), nullable=False),
            sa.Column('last_Name', sa.String(length=256), nullable=True),
            sa.Column('email', sa.String(length=150), nullable=False),
            sa.Column('password', sa.String(length=256), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email')
        )

    # Create user_profiles table if it doesn't exist
    if 'user_profiles' not in existing_tables:
        op.create_table('user_profiles',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
            sa.Column('business_id', UUID(), sa.ForeignKey('businesses.id', ondelete='CASCADE'), nullable=False),
            sa.Column('role', sa.Enum('admin', 'teacher', 'student', 'developer', 'moderator', name='userrole'), nullable=False),
            sa.Column('first_name', sa.String(100), nullable=True),
            sa.Column('last_name', sa.String(100), nullable=True),
            sa.Column('phone', sa.String(20), nullable=True),
            sa.Column('preferences', sa.JSON(), nullable=True),
            sa.Column('meta_data', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('last_active', sa.DateTime(timezone=True), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create memories table if it doesn't exist
    if 'memories' not in existing_tables:
        op.create_table('memories',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('business_id', UUID(), sa.ForeignKey('businesses.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('type', sa.Enum('UserProfile', 'Codex', 'Room127', 'Suspense', 'File', 'AuditLog', 'DeveloperLog', 'text', 'image', 'audio', 'video', 'document', name='memorytype'), nullable=False),
            sa.Column('tags', sa.ARRAY(sa.String()), nullable=True),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('embedding', sa.ARRAY(sa.Float()), nullable=True),
            sa.Column('date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('memory_metadata', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create room_127_logs table if it doesn't exist
    if 'room_127_logs' not in existing_tables:
        op.create_table('room_127_logs',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('context', sa.String(50), nullable=False),
            sa.Column('feedback', sa.JSON(), nullable=True),
            sa.Column('meta_data', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create module_states table if it doesn't exist
    if 'module_states' not in existing_tables:
        op.create_table('module_states',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('module_id', sa.String(36), nullable=False),
            sa.Column('state', sa.JSON(), nullable=False),
            sa.Column('meta_data', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create codex_logs table if it doesn't exist
    if 'codex_logs' not in existing_tables:
        op.create_table('codex_logs',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('context', sa.String(50), nullable=False),
            sa.Column('analysis', sa.JSON(), nullable=True),
            sa.Column('meta_data', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create developer_logs table if it doesn't exist
    if 'developer_logs' not in existing_tables:
        op.create_table('developer_logs',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('context', sa.String(50), nullable=False),
            sa.Column('log_level', sa.String(20), nullable=False),
            sa.Column('meta_data', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create audit_logs table if it doesn't exist
    if 'audit_logs' not in existing_tables:
        op.create_table('audit_logs',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('action', sa.String(100), nullable=False),
            sa.Column('details', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create tickets table if it doesn't exist
    if 'tickets' not in existing_tables:
        op.create_table('tickets',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('title', sa.String(200), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('status', sa.Enum('open', 'in_progress', 'review', 'resolved', 'closed', name='ticketstatus'), nullable=False),
            sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='ticketpriority'), nullable=False),
            sa.Column('type', sa.Enum('bug', 'feature', 'enhancement', 'documentation', 'support', name='tickettype'), nullable=False),
            sa.Column('created_by', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('assigned_to', UUID(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('tags', sa.JSON(), nullable=True),
            sa.Column('meta_data', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create ticket_comments table if it doesn't exist
    if 'ticket_comments' not in existing_tables:
        op.create_table('ticket_comments',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('ticket_id', sa.String(36), sa.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('meta_data', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create ticket_history table if it doesn't exist
    if 'ticket_history' not in existing_tables:
        op.create_table('ticket_history',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('ticket_id', sa.String(36), sa.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('action', sa.String(50), nullable=False),
            sa.Column('changes', sa.JSON(), nullable=False),
            sa.Column('meta_data', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create roles table if it doesn't exist
    if 'roles' not in existing_tables:
        op.create_table('roles',
            sa.Column('id', sa.BigInteger(), nullable=False),
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.Column('description', sa.String(length=200), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create permissions table if it doesn't exist
    if 'permissions' not in existing_tables:
        op.create_table('permissions',
            sa.Column('id', sa.BigInteger(), nullable=False),
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.Column('description', sa.String(length=200), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create role_permissions table if it doesn't exist
    if 'role_permissions' not in existing_tables:
        op.create_table('role_permissions',
            sa.Column('role_id', sa.BigInteger(), nullable=False),
            sa.Column('permission_id', sa.BigInteger(), nullable=False),
            sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
            sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
            sa.PrimaryKeyConstraint('role_id', 'permission_id')
        )

    # Create user_roles table if it doesn't exist
    if 'user_roles' not in existing_tables:
        op.create_table('user_roles',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('user_id', UUID(), nullable=False),
            sa.Column('role_id', sa.BigInteger(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # Create user_consent table if it doesn't exist
    if 'user_consent' not in existing_tables:
        op.create_table('user_consent',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('user_id', UUID(), nullable=True),
            sa.Column('consent_given', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create feedback_logs table if it doesn't exist
    if 'feedback_logs' not in existing_tables:
        op.create_table('feedback_logs',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('user_id', UUID(), nullable=True),
            sa.Column('source', sa.String(length=50), nullable=True),
            sa.Column('feedback_text', sa.Text(), nullable=True),
            sa.Column('related_module', sa.String(length=100), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create comprehension_logs table if it doesn't exist
    if 'comprehension_logs' not in existing_tables:
        op.create_table('comprehension_logs',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('user_id', UUID(), nullable=True),
            sa.Column('material', sa.Text(), nullable=True),
            sa.Column('comprehension_score', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create vocabulary_logs table if it doesn't exist
    if 'vocabulary_logs' not in existing_tables:
        op.create_table('vocabulary_logs',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('user_id', UUID(), nullable=True),
            sa.Column('word', sa.String(length=100), nullable=True),
            sa.Column('context', sa.Text(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create grammar_logs table if it doesn't exist
    if 'grammar_logs' not in existing_tables:
        op.create_table('grammar_logs',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('user_id', UUID(), nullable=True),
            sa.Column('error_type', sa.String(length=50), nullable=True),
            sa.Column('correction', sa.Text(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create pronunciation_logs table if it doesn't exist
    if 'pronunciation_logs' not in existing_tables:
        op.create_table('pronunciation_logs',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('user_id', UUID(), nullable=True),
            sa.Column('word', sa.String(length=100), nullable=True),
            sa.Column('score', sa.Float(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create roleplay_sessions table if it doesn't exist
    if 'roleplay_sessions' not in existing_tables:
        op.create_table('roleplay_sessions',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('user_id', UUID(), nullable=True),
            sa.Column('scenario', sa.String(length=200), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create audio_files table if it doesn't exist
    if 'audio_files' not in existing_tables:
        op.create_table('audio_files',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('user_id', UUID(), nullable=True),
            sa.Column('filename', sa.String(length=200), nullable=True),
            sa.Column('file_path', sa.String(length=500), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create learning_modules table if it doesn't exist
    if 'learning_modules' not in existing_tables:
        op.create_table('learning_modules',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create lessons table if it doesn't exist
    if 'lessons' not in existing_tables:
        op.create_table('lessons',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('module_id', UUID(), nullable=True),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['module_id'], ['learning_modules.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create integrations table if it doesn't exist
    if 'integrations' not in existing_tables:
        op.create_table('integrations',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('api_key', sa.String(length=200), nullable=True),
            sa.Column('settings', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create scraping_sources table if it doesn't exist
    if 'scraping_sources' not in existing_tables:
        op.create_table('scraping_sources',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('url', sa.String(length=500), nullable=False),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create scraped_contents table if it doesn't exist
    if 'scraped_contents' not in existing_tables:
        op.create_table('scraped_contents',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('source_id', UUID(), nullable=True),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['source_id'], ['scraping_sources.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create files table if it doesn't exist
    if 'files' not in existing_tables:
        op.create_table('files',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('filename', sa.String(), nullable=False),
            sa.Column('s3_url', sa.String(), nullable=False),
            sa.Column('uploaded_by', sa.String(), nullable=False),
            sa.Column('folder', sa.String(), nullable=False),
            sa.Column('filetype', sa.String(), nullable=False),
            sa.Column('uploaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('user_id', UUID(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create activities table if it doesn't exist
    if 'activities' not in existing_tables:
        op.create_table('activities',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('user_id', UUID(), nullable=True),
            sa.Column('activity_type', sa.String(length=50), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create license_keys table if it doesn't exist
    if 'license_keys' not in existing_tables:
        op.create_table('license_keys',
            sa.Column('id', UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
            sa.Column('key', sa.String(length=100), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create chatbot_memories table if it doesn't exist
    if 'chatbot_memories' not in existing_tables:
        op.create_table('chatbot_memories',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('business_id', UUID(), sa.ForeignKey('businesses.id', ondelete='CASCADE'), nullable=False),
            sa.Column('conversation_id', sa.String(36), nullable=False),
            sa.Column('type', sa.String(50), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('memory_metadata', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create conversation_contexts table if it doesn't exist
    if 'conversation_contexts' not in existing_tables:
        op.create_table('conversation_contexts',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('business_id', sa.String(36), nullable=False),
            sa.Column('context', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create chat_histories table if it doesn't exist
    if 'chat_histories' not in existing_tables:
        op.create_table('chat_histories',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('context', sa.String(50), nullable=False),
            sa.Column('model_source', sa.String(50), nullable=False),
            sa.Column('messages', sa.JSON(), nullable=False),
            sa.Column('chat_metadata', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('is_archived', sa.Integer(), nullable=True),
            sa.Column('last_message_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('message', sa.Text(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )

    # Create language_test_audio table if it doesn't exist
    if 'language_test_audio' not in existing_tables:
        op.create_table('language_test_audio',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('section', sa.String(), nullable=True),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('topic', sa.String(), nullable=True),
            sa.Column('question_type', sa.String(), nullable=True),
            sa.Column('language_level', sa.String(), nullable=True),
            sa.Column('rubric_score', sa.Float(), nullable=True),
            sa.Column('file_path', sa.String(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create diagnostic_results table if it doesn't exist
    if 'diagnostic_results' not in existing_tables:
        op.create_table('diagnostic_results',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('student_id', sa.String(), nullable=True),
            sa.Column('score', sa.Integer(), nullable=True),
            sa.Column('level', sa.String(), nullable=True),
            sa.Column('learning_content', sa.Text(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create arbitration table if it doesn't exist
    if 'arbitration' not in existing_tables:
        op.create_table('arbitration',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('request_id', sa.String(36), nullable=True),
            sa.Column('content', sa.String(), nullable=False),
            sa.Column('context', sa.String(), nullable=False),
            sa.Column('model_source', sa.String(), nullable=False),
            sa.Column('status', sa.String(), nullable=False),
            sa.Column('priority', sa.Integer(), nullable=True),
            sa.Column('review_notes', sa.String(), nullable=True),
            sa.Column('arbitration_metadata', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('reviewed_by', sa.String(), nullable=True),
            sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Create subai_logs table if it doesn't exist
    if 'subai_logs' not in existing_tables:
        op.create_table('subai_logs',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('prompt', sa.String(), nullable=False),
            sa.Column('model', sa.String(50), nullable=False),
            sa.Column('response', sa.JSON(), nullable=False),
            sa.Column('subAi_metadata', sa.JSON(), nullable=True),
            sa.Column('message', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('subai_logs')
    op.drop_table('arbitration')
    op.drop_table('diagnostic_results')
    op.drop_table('language_test_audio')
    op.drop_table('chat_histories')
    op.drop_table('conversation_contexts')
    op.drop_table('chatbot_memories')
    op.drop_table('license_keys')
    op.drop_table('activities')
    op.drop_table('files')
    op.drop_table('scraped_contents')
    op.drop_table('scraping_sources')
    op.drop_table('integrations')
    op.drop_table('lessons')
    op.drop_table('learning_modules')
    op.drop_table('audio_files')
    op.drop_table('roleplay_sessions')
    op.drop_table('pronunciation_logs')
    op.drop_table('grammar_logs')
    op.drop_table('vocabulary_logs')
    op.drop_table('comprehension_logs')
    op.drop_table('feedback_logs')
    op.drop_table('user_consent')
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('ticket_history')
    op.drop_table('ticket_comments')
    op.drop_table('tickets')
    op.drop_table('audit_logs')
    op.drop_table('developer_logs')
    op.drop_table('codex_logs')
    op.drop_table('module_states')
    op.drop_table('room_127_logs')
    op.drop_table('memories')
    op.drop_table('user_profiles')
    op.drop_table('users')
    op.drop_table('businesses')
    # Drop the extension last
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"') 