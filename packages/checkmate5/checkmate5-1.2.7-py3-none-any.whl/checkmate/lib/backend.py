"""
Thin wrapper around BlitzDB's SQL backend to support SQLite/SQL engines.
"""

from contextlib import contextmanager
from blitzdb.backends.sql import Backend as BlitzSQLBackend


class SQLBackend:
    def __init__(self, engine):
        """
        Initialize with a SQLAlchemy engine. BlitzDB handles schema creation.
        """
        self.engine = engine
        self.backend = BlitzSQLBackend(engine)
        # Ensure tables exist
        self.backend.init_schema()

    @contextmanager
    def transaction(self):
        with self.backend.transaction():
            yield

    def save(self, obj):
        return self.backend.save(obj)

    def commit(self):
        return self.backend.commit()

    def get(self, cls, query, include=None):
        return self.backend.get(cls, query, include=include)

    def filter(self, cls, query, **kwargs):
        return self.backend.filter(cls, query, **kwargs)

    def update(self, obj, fields):
        return self.backend.update(obj, fields)

    def serialize(self, obj):
        return self.backend.serialize(obj)

    @property
    def connection(self):
        return self.backend.connection

    def get_table(self, model):
        # BlitzDB SQL backend keeps metadata in backend tables
        if hasattr(self.backend, "get_table"):
            return self.backend.get_table(model)
        if hasattr(self.backend, "table"):
            return self.backend.table(model)
        raise NotImplementedError("Underlying backend does not expose get_table")


