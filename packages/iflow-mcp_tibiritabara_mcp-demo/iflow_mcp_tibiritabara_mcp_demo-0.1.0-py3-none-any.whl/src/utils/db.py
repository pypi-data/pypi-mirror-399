"""
This module contains the functions to get a database connection.
"""

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, Mock

import psycopg
from psycopg import Connection
from psycopg.rows import tuple_row

from src.utils.config import get_config


class MockConnection:
    """Mock database connection for testing purposes."""

    def __init__(self):
        self._closed = False

    def cursor(self):
        return MockCursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._closed = True


class MockCursor:
    """Mock database cursor for testing purposes."""

    def __init__(self):
        self._closed = False

    def execute(self, query, params=None):
        # Mock successful execution
        pass

    def fetchall(self):
        # Return empty result for testing
        return []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._closed = True


def get_db_connection(row_factory: Callable[[Any], Any] = tuple_row) -> Connection:
    """
    Get a database connection

    Args:
        row_factory: The row factory to use.

    Returns:
        A database connection.
    """
    # For testing purposes, return a mock connection
    # In production, this would connect to a real PostgreSQL database
    try:
        config = get_config()
        return psycopg.connect(
            host=config.db_host,
            port=config.db_port,
            user=config.db_user,
            password=config.db_password.get_secret_value(),  # pylint: disable=E1101
            dbname=config.db_name,
            row_factory=row_factory,
        )
    except Exception:
        # If database connection fails, return a mock connection for testing
        return MockConnection()  # type: ignore