import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- ADIÇÃO SÊNIOR: Adicionar o diretório src ao path ---
# Sem isso, o Alembic não consegue importar 'src.models'
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# --- IMPORTAR SEUS MODELOS ---
from src.config.settings import DATABASE_URL
from src.models.base import Base
from src.models.product import Product  # Importar para registrar
from src.models.sale import Sale        # Importar para registrar

config = context.config

# Sobrescreve a URL do arquivo .ini com a URL do nosso settings.py
# Isso garante que o projeto todo use a mesma fonte de verdade.
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- ALTERAÇÃO: Conectar o metadata ---
# O original é: target_metadata = None
target_metadata = Base.metadata



# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
