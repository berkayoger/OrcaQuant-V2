from __future__ import with_statement

from alembic import context
from flask import current_app

config = context.config

target_db = current_app.extensions["migrate"].db
target_metadata = target_db.metadata


def get_engine():
    return target_db.get_engine()


def run_migrations_offline():
    url = str(get_engine().url)
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = get_engine()
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
