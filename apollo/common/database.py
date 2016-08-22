import os
from flask import g, current_app
from cassandra.cqlengine.management import sync_table, sync_type
from cassandra.cqlengine import connection


def connect():
    """Connects to the specific database."""
    connection.setup([current_app.config.get('DATABASE_IP', '127.0.0.1')],
                     current_app.config.get('DATABASE_KEYSPACE', 'dev'),
                     protocol_version=3)
    return connection.get_session()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect()
    return db


def init_db(models=None, types=None):
    """
    To sync the models to the database.
    *Note: synchronizing models causes schema changes, and should be done with caution.
    Please see the discussion in cassandra.cqlengine.management - Schema management for cqlengine for considerations.
    """
    get_db()
    if models:
        for model in models:
            sync_table(model)
    if types:
        ks = current_app.config.get('DATABASE_KEYSPACE', 'dev')
        for t in types:
            sync_type(ks, t)

