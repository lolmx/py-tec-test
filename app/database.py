from sqlalchemy import create_engine, Connection

from .config import get_settings

engine = create_engine(get_settings().database_url)


class DatabaseConnection:
    def __init__(self):
        self.connection = engine.connect()

    def __enter__(self) -> Connection:
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
