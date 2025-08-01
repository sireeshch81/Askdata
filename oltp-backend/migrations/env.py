import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Build the URL from environment variables
user = os.environ["MYSQL_DW_USER"]
password = os.environ["MYSQL_DW_PASSWORD"]
host = os.environ["MYSQL_DW_HOST"]
port = os.environ["MYSQL_DW_PORT"]
database = os.environ["MYSQL_DW_DATABASE"]

url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

config = context.config
config.set_main_option("sqlalchemy.url", url)


# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# add your model's MetaData object here
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import (
    Base,
    Member,
    CreditCard,
    PaymentHistory,
    FinancialHealthMetric,
    FinancialProduct,
)  # noqa

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    section = config.get_section(config.config_ini_section)
    section['url'] = config.get_main_option("sqlalchemy.url")
    print(section)
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

