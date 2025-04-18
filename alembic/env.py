from logging.config import fileConfig
import os
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.db.database import BASE
from app.models import users


load_dotenv(dotenv_path="app/.env")


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")

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
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
