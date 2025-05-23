from logging.config import fileConfig
import os
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool, text
from alembic import context
from app.db.database import BASE
from app.models.users import User, UserConsent
from app.models.audio_file import AudioFile
from app.models.comprehension_log import ComprehensionLog
from app.models.feedback_log import FeedbackLog
from app.models.grammar_log import GrammarLog
from app.models.integration import Integration
from app.models.learning_module import LearningModule
from app.models.lesson import Lesson
from app.models.pronunciation_log import PronunciationLog
from app.models.roleplay_session import RolePlaySession
from app.models.scraped_content import ScrapedContent
from app.models.scraping_source import ScrapingSource
from app.models.vocabulary_log import VocabularyLog
from app.models.role import Role, UserRole, Permission
from app.models.licenskey import LicenseKey
from app.models.Diagnostic import DiagnosticResult
from app.models.files import File
from app.models.LanguageTest import LanguageTest
from app.models.memory import UserProfile, ModuleState, CodexLog, Room127Log, DeveloperLog, AuditLog, Memory
from app.models.ticket_models import Ticket, TicketComment, TicketHistory
from app.models.chat_history import ChatHistory
from app.models.chatbot import ChatbotMemory, ConversationContext
from app.models.business import Business
from app.models.arbitration import Arbitration
from app.models.subai_log import SubAILog
from app.models.activity import Activity

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in environment variables")

# this is the Alembic Config object
config = context.config

# ✅ Inject DATABASE_URL into Alembic config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata object
target_metadata = BASE.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Drop existing alembic_version table if it exists
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Enable type comparison
            compare_server_default=True,  # Enable server default comparison
            version_table='alembic_version',  # Explicitly set version table name
            version_table_schema=None,  # Use default schema
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
