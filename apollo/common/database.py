import os
from flask import g
from cassandra.cluster import Cluster
from cassandra.cqlengine.management import sync_table


def connect_db():
    """Connects to the specific database."""
    cluster = Cluster([os.getenv('DATABASE_IP', '127.0.0.1')], protocol_version=3)
    session = cluster.connect()
    session.set_keyspace(os.getenv('DATABASE_KEYSPACE', 'dev'))
    return session


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db


def init_db(models=None):
    """
    To sync the models to the database.
    *Note: synchronizing models causes schema changes, and should be done with caution.
    Please see the discussion in cassandra.cqlengine.management - Schema management for cqlengine for considerations.
    """
    db = get_db()
    for model in models:
        sync_table(model)

