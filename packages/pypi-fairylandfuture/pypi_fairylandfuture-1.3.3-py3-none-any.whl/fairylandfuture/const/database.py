# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-12-31 18:53:58 UTC+08:00
"""

import psycopg.sql


class SQLKeywordConst:
    """
    A class that stores constant SQL keyword definitions for specific
    database dialects, supporting ease of use and readability in
    query construction.

    This class focuses on providing pre-defined constants for SQL keywords
    in specific database dialects to enhance developer productivity and
    minimize repetitive SQL typing errors.
    """

    class PostgreSQL:
        """
        Provides predefined SQL command templates as reusable constants for PostgreSQL interactions.

        This class serves as a centralized repository for SQL commands frequently used in
        PostgreSQL database operations. The purpose is to enhance code readability and reusability
        by storing these commands as immutable, predefined templates.
        """

        SELECT: psycopg.sql.Composed = psycopg.sql.SQL("SELECT")
        INSERT_INTO: psycopg.sql.Composed = psycopg.sql.SQL("INSERT INTO")
        UPDATE: psycopg.sql.Composed = psycopg.sql.SQL("UPDATE")
        DELETE_FROM: psycopg.sql.Composed = psycopg.sql.SQL("DELETE FROM")
        VALUES: psycopg.sql.Composed = psycopg.sql.SQL("VALUES")
        RETURNING: psycopg.sql.Composed = psycopg.sql.SQL("RETURNING")
        ON_CONFLICT: psycopg.sql.Composed = psycopg.sql.SQL("ON CONFLICT")
        DO_UPDATE_SET: psycopg.sql.Composed = psycopg.sql.SQL("DO UPDATE SET")
        DO_NOTHING: psycopg.sql.Composed = psycopg.sql.SQL("DO NOTHING")
        EXCLUDED: psycopg.sql.Composed = psycopg.sql.SQL("EXCLUDED")
