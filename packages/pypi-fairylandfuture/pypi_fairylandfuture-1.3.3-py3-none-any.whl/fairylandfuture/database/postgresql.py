# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-12-29 19:46:12 UTC+08:00
"""

import contextlib
import copy
import datetime
import time
import typing as t

import psycopg
import psycopg.sql
from psycopg.rows import dict_row, tuple_row

from fairylandfuture import logger
from fairylandfuture.const.database import SQLKeywordConst
from fairylandfuture.models import BaseModelPostgreSQL
from fairylandfuture.structures.database import PostgreSQLExecuteStructure
from fairylandfuture.utils.strings import StringUtils

MODEL_ORM_TYPE = t.TypeVar("MODEL_ORM_TYPE", bound="BaseModelPostgreSQL")


class PostgreSQLConnector:
    """
    Provides functionality to interact with a PostgreSQL database using psycopg.

    This class manages the connection lifecycle, supports connection pooling, and provides high-level
    APIs for executing SQL queries. It ensures reconnection strategies to maintain a reliable
    connection at all times. Optionally, it supports transaction management, commit, and rollback
    operations.

    The class is designed to be used as both a context manager and a standalone instance.

    :ivar autocommit: Specifies whether autocommit mode is enabled for transactions.
    :type autocommit: bool
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str,
        timezone: str = "Asia/Shanghai",
        keepalive_idle: int = 60,
        keepalive_interval: int = 10,
        keepalive_count: int = 5,
        connect_timeout: int = 10,
        autocommit: bool = False,
        **kwargs,
    ):
        self.autocommit = autocommit
        self.__connection_params = {
            "host": host,
            "port": port,
            "user": username,
            "password": password,
            "dbname": database,
            "connect_timeout": connect_timeout,
            "keepalives_idle": keepalive_idle,
            "keepalives_interval": keepalive_interval,
            "keepalives_count": keepalive_count,
            "options": f"-c timezone={timezone}",
            **kwargs,
        }
        self.__connection: t.Optional[psycopg.Connection] = None

        self.__connection_id: int = 0
        self.__last_activity_timestamp: float = 0.0

    def __enter__(self):
        self.ensure_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        """
        Provides a property to manage and retrieve a PostgreSQL connection. Ensures
        that the connection is active and re-establishes it if it is lost. Tracks the
        timestamp of the last activity for monitoring purposes. Handles connection
        lifecycle management and logging of errors or warnings during connection issues.

        :return: The active PostgreSQL connection.
        :rtype: Any
        """
        while True:
            try:
                if self.__connection is None or self.__connection.closed:
                    self.__connect()
                else:
                    if not self.__is_connection_alive():
                        logger.warning("PostgreSQL connection lost, reconnecting...")
                        self.__reconnect()

                self.__last_activity_timestamp = datetime.datetime.now().timestamp()
                return self.__connection
            except Exception as err:
                logger.error(f"Error obtaining PostgreSQL connection: {err}")
                time.sleep(2)

    def __connect(self):
        """
        Establishes a connection to the PostgreSQL database using the provided connection
        parameters. This method attempts to create the database connection and logs its
        status.

        If an exception occurs during connection initialization, it logs the error and
        raises the exception to be handled by the calling code.

        :return: None
        :rtype: None

        :raises: Exception
        """
        try:
            self.__connection = psycopg.connect(**self.__connection_params, autocommit=self.autocommit)
            self.__connection_id += 1
            self.__last_activity_timestamp = datetime.datetime.now().timestamp()
            logger.info(f"PostgreSQL connected successfully, connection id: {self.__connection_id}")
        except Exception as err:
            logger.error(f"PostgreSQL connection error: {err}")
            raise

    def __is_connection_alive(self) -> bool:
        """
        Checks if the database connection is alive by executing a simple query.

        This method verifies the health of the current database connection by ensuring
        it exists, is not marked as closed, and can successfully execute a query. If
        the connection is invalid or an exception occurs during the query execution,
        it logs the error and returns False.

        :return: Returns True if the database connection is alive and functional,
            otherwise returns False.
        :rtype: bool
        """
        try:
            if self.__connection is None or self.__connection.closed:
                return False
            with self.__connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchall()
            return True
        except Exception as err:
            logger.error(f"PostgreSQL connection id {self.__connection_id} is not alive: {err}")
            return False

    def __reconnect(self):
        self.close()
        self.__connect()

    def ensure_connection(self):
        _ = self.connection

    def close(self):
        """
        Closes the current PostgreSQL connection if it is open.

        The method attempts to close the connection to PostgreSQL if the connection
        exists and is not already closed. It ensures proper cleanup by setting the
        connection attribute to None after successful closure or in the event of
        an error during closure. Logs informational and error messages as appropriate.

        :return: None
        :rtype: None
        """
        if self.__connection and not self.__connection.closed:
            try:
                self.__connection.close()
                logger.info(f"PostgreSQL connection id {self.__connection_id} closed.")
            except Exception as err:
                logger.error(f"Error closing PostgreSQL connection id {self.__connection_id}: {err}")
            finally:
                self.__connection = None

    def get_cursor(self, /, *, row_factory: t.Optional[psycopg.rows.RowFactory] = None) -> psycopg.Cursor:
        """
        Retrieves a cursor object for interacting with the database.

        This method returns a new cursor object that can be used to execute
        queries against the database. If a specific row factory is provided,
        the cursor will utilize it for formatting rows. Otherwise, the default
        formatting will be applied.

        :param row_factory: Optional row factory to determine the format for
            returned rows. If None, the default formatting is used.
        :type row_factory: t.Optional[psycopg.rows.RowFactory]
        :return: A cursor object for interacting with the database.
        :rtype: psycopg.Cursor
        """
        if row_factory:
            return self.connection.cursor(row_factory=row_factory)
        return self.connection.cursor()

    def commit(self):
        """
        Commits the current transaction for the associated database connection. This method
        ensures that all changes within the scope of the transaction are saved permanently
        to the database. If an error occurs during the commit process, it will log the
        error and re-raise the original exception.

        :return: None
        :rtype: None
        """
        try:
            self.connection.commit()
            logger.debug(f"Transaction committed.")
        except Exception as err:
            logger.error(f"Error committing PostgreSQL connection id {self.__connection_id}: {err}")
            raise err

    def rollback(self):
        """
        Rolls back the current transaction on the database connection.

        Provides functionality to undo the current transaction by reverting
        all operations performed during the transaction. This is particularly
        useful in scenarios where an error occurs, and the database state needs
        to remain consistent.

        :raises Exception: If an error occurs while rolling back the transaction.
        :return: None
        :rtype: None
        """
        try:
            self.connection.rollback()
            logger.debug(f"Transaction rolled back.")
        except Exception as err:
            logger.error(f"Error rolling back PostgreSQL connection id {self.__connection_id}: {err}")
            raise

    @contextlib.contextmanager
    def transaction(self):
        """
        Manages a context for executing a transaction using a PostgreSQL connection. This function
        provides a way to ensure that a transaction is properly opened, committed, or rolled back
        in case of an error. When invoked, it yields a database connection object that can be used
        to perform database operations within the transaction bounds.

        If an exception occurs during the transaction, the transaction is rolled back, an error
        is logged, and the exception is re-raised.

        :return: Yields the database connection object for executing database commands within the
            transaction context.
        :rtype: Connection
        """
        connection = self.connection
        try:
            with connection.transaction():
                yield connection
        except Exception as err:
            logger.error(f"Transaction error on PostgreSQL connection id {self.__connection_id}: {err}")
            raise


class PostgreSQLRepository:
    """
    Provides functionality to interact with a PostgreSQL database using queries and execute
    operations in an efficient and structured manner.

    This class facilitates executing individual queries, batch operations, and retrieving data
    in multiple row formats according to the desired output. It supports logging and error
    handling, making it suitable for production use cases.

    :ivar connector: Provides the database connection and methods for cursor management.
    :type connector: PostgreSQLConnector
    """

    def __init__(self, connector: PostgreSQLConnector):
        self.connector = connector

    def execute(self, exec: PostgreSQLExecuteStructure, commit: bool = False) -> psycopg.Cursor[t.Any]:
        """
        Executes a PostgreSQL query using the provided execution structure. Optionally commits the transaction if the
        commit flag is set to True. The query and its parameters are logged for debugging purposes. Any errors during
        execution are caught, logged, and re-raised.

        :param exec: The structure containing the PostgreSQL query object and the variables  to be substituted into the query.
        :type exec: PostgreSQLExecuteStructure
        :param commit: A boolean flag indicating whether to commit the transaction after executing the query. Defaults to False.
        :type commit: bool
        :return: The cursor object containing the result of the executed query.
        :rtype: psycopg.Cursor[t.Any]
        :raises Exception: If an error occurs during the execution of the PostgreSQL query.
        """
        cursor = self.connector.get_cursor(row_factory=dict_row)
        try:
            logger.debug(f"Executing PostgreSQL query: {exec.query.as_string()} with vars: {exec.vars}")
            cursor.execute(exec.query, exec.vars)
            if commit:
                self.connector.commit()
            return cursor
        except Exception as error:
            logger.error(f"Error executing PostgreSQL query: {error}")
            raise

    def executemany(self, exec: PostgreSQLExecuteStructure, batch_size: int = 1000, commit_interval: int = 10000, show_progress: bool = True):
        """
        Executes a batch of database operations using the provided PostgreSQL query and variables. The function
        splits the operations into batches, executes each in sequence, and handles committing to the database
        periodically based on the specified commit interval. Progress logging and timing information can also
        be displayed if enabled.

        :param exec: The structure containing the PostgreSQL query and corresponding variables for parameterized
            execution.
        :type exec: PostgreSQLExecuteStructure
        :param batch_size: The number of rows to execute in a single batch. Defaults to 1000.
        :type batch_size: int
        :param commit_interval: The interval, in rows, at which to commit the database transaction. Defaults
            to 10000.
        :type commit_interval: int
        :param show_progress: Whether to display progress information, including rows processed and elapsed time.
            Defaults to True.
        :type show_progress: bool
        :return: The total number of rows processed during the batch execution.
        :rtype: int
        """
        total_rows: int = len(exec.vars) if exec.vars else 0
        processed_rows: int = 0
        start_time: float = datetime.datetime.now().timestamp()

        cursor = self.connector.get_cursor()
        try:
            for i in range(0, total_rows, batch_size):
                batch = exec.vars[i : i + batch_size]

                self.connector.ensure_connection()

                logger.debug(f"Executing batch of size {len(batch)} for PostgreSQL query: {StringUtils.format(exec.query.as_string(), "SQL")}")
                cursor.executemany(exec.query, batch)
                processed_rows += len(batch)

                if processed_rows % commit_interval == 0 or processed_rows == total_rows:
                    self.connector.commit()

                    if show_progress:
                        elapsed = datetime.datetime.now().timestamp() - start_time
                        logger.info(f"Executed {processed_rows}/{total_rows} rows in {elapsed:.2f} seconds.")

            total_elapsed = datetime.datetime.now().timestamp() - start_time
            logger.info(f"Completed executing {total_rows} rows in {total_elapsed:.2f} seconds, average {total_rows / total_elapsed:.2f} rows/second.")
            return processed_rows
        except Exception as error:
            logger.error(f"Error executing PostgreSQL batch query: {error}")
            raise

    @t.overload
    def fetchone(self, exec: PostgreSQLExecuteStructure, /, *, as_dict: t.Literal[True] = True) -> t.Optional[t.Dict[str, t.Any]]: ...

    @t.overload
    def fetchone(self, exec: PostgreSQLExecuteStructure, /, *, as_dict: t.Literal[False] = False) -> t.Optional[t.Tuple[t.Any, ...]]: ...

    @t.overload
    def fetchone(self, exec: PostgreSQLExecuteStructure, /, *, clazz: t.Type[MODEL_ORM_TYPE]) -> t.Optional[MODEL_ORM_TYPE]: ...

    def fetchone(
        self,
        exec: PostgreSQLExecuteStructure,
        /,
        *,
        as_dict: bool = True,
        clazz: t.Optional[t.Type[MODEL_ORM_TYPE]] = None,
    ) -> t.Dict[str, t.Any] | t.Tuple[t.Any, ...] | MODEL_ORM_TYPE | None:
        """
        Fetches a single row from the PostgreSQL database using the provided query structure.

        This method executes a provided SQL query using a cursor obtained from the database
        connection. The row fetched can be returned either as a dictionary, a tuple, or as an
        instance of a specified ORM model. If no rows are found, it will return None.

        :param exec: The structure containing the SQL query and its variables to execute.
        :type exec: PostgreSQLExecuteStructure
        :param as_dict: Whether to fetch the row as a dictionary. Defaults to True.
        :type as_dict: bool
        :param clazz: A class (typically ORM model) to transform the row into. If None, the
            row will not be transformed into a class instance.
        :type clazz: t.Optional[t.Type[MODEL_ORM_TYPE]]
        :return: The fetched row, which can be a dictionary (`as_dict=True`), a tuple
            (`as_dict=False`), an instance of the specified class (`clazz` is provided), or
            None if no row is found.
        :rtype: t.Dict[str, t.Any] | t.Tuple[t.Any, ...] | MODEL_ORM_TYPE | None
        """
        row_factory = dict_row if (as_dict or clazz) else tuple_row
        cursor = self.connector.get_cursor(row_factory=row_factory)

        logger.debug(f"Fetching one row for PostgreSQL query: {StringUtils.format(exec.query.as_string(), "SQL")} with vars: {exec.vars}")

        cursor.execute(exec.query, exec.vars)
        row = cursor.fetchone()

        logger.debug(f"Fetched one row: {row}")

        if clazz:
            return clazz(**row)
        return row

    @t.overload
    def fetchmany(
        self,
        exec: PostgreSQLExecuteStructure,
        /,
        *,
        size: int = 100,
        as_dict: t.Literal[True] = True,
    ) -> t.Generator[t.List[t.Dict[str, t.Any]], None, None]: ...

    @t.overload
    def fetchmany(
        self,
        exec: PostgreSQLExecuteStructure,
        /,
        *,
        size: int = 100,
        as_dict: t.Literal[False] = False,
    ) -> t.Generator[t.List[t.Tuple[t.Any, ...]], None, None]: ...

    @t.overload
    def fetchmany(
        self,
        exec: PostgreSQLExecuteStructure,
        /,
        *,
        size: int = 100,
        clazz: t.Type[MODEL_ORM_TYPE],
    ) -> t.Generator[t.List[MODEL_ORM_TYPE], None, None]: ...

    def fetchmany(
        self,
        exec: PostgreSQLExecuteStructure,
        /,
        *,
        size: int = 100,
        as_dict: bool = True,
        clazz: t.Optional[t.Type[MODEL_ORM_TYPE]] = None,
    ) -> t.Generator[t.List[t.Dict[str, t.Any]] | t.List[t.Tuple[t.Any, ...] | t.List[MODEL_ORM_TYPE]], None, None]:
        """
        Fetches and yields batches of rows from a database query result.

        The function executes a SQL query and retrieves results in chunks of the specified
        size (`size` parameter). The output format of the rows can either be dictionaries,
        tuples, or instances of a specified data model class (`clazz` parameter). This allows
        flexible handling of database query results for different use cases.

        The generator yields each batch of rows as they are fetched from the database.

        :param exec: The structure containing the SQL query and its associated variables
            to execute.
        :type exec: PostgreSQLExecuteStructure
        :param size: The number of rows to fetch per batch. Defaults to 100.
        :type size: int
        :param as_dict: Boolean to decide if the rows should be returned as dictionaries. If set
            to `True`, each row is converted into a dictionary. Defaults to `True`.
        :type as_dict: bool
        :param clazz: An optional ORM class type. If specified, each row is cast into an
            instance of the given class. Defaults to `None`.
        :type clazz: Optional[Type[MODEL_ORM_TYPE]]
        :return: A generator that yields batches of rows in the selected format (dictionaries,
            tuples, or class instances).
        :rtype: Generator[List[Dict[str, Any]] | List[Tuple[Any, ...]] | List[MODEL_ORM_TYPE], None, None]
        """
        row_factory = dict_row if (as_dict or clazz) else tuple_row
        cursor = self.connector.get_cursor(row_factory=row_factory)
        cursor.execute(exec.query, exec.vars)

        while True:
            rows = cursor.fetchmany(size)
            if not rows:
                break
            if clazz:
                yield [clazz(**row) for row in rows]
            else:
                yield rows

    @t.overload
    def insert(self, data: MODEL_ORM_TYPE) -> MODEL_ORM_TYPE | None: ...

    @t.overload
    def insert(self, data: t.Mapping[str, t.Any], /, *, table: str, schema: t.Optional[str] = None) -> t.Mapping[str, t.Any] | None: ...

    def insert(
        self,
        data: t.Mapping[str, t.Any] | MODEL_ORM_TYPE,
        /,
        *,
        table: t.Optional[str] = None,
        schema: t.Optional[str] = None,
        on_conflict: t.Optional[t.Sequence[str]] = None,
        update_now_fields: t.Sequence[str] = ("updated_at",),
        commit: bool = True,
    ) -> MODEL_ORM_TYPE | t.Mapping[str, t.Any] | None:
        """
        Insert a row into a PostgreSQL table with handling for conflict scenarios and additional features.

        This function supports inserting data into a specified PostgreSQL table and schema, with optional
        handling for conflicts that may arise during the insertion process. It also allows for updating
        specific fields when conflicts occur and supports timestamp-based field updates. The function can
        operate on either ORM models or raw mappings.

        :param data: The data to be inserted. It can be an ORM model or a mapping of column names to values.
        :type data: t.Mapping[str, t.Any] | MODEL_ORM_TYPE
        :param table: The name of the target table. If not provided, it is inferred from the ORM model if
            `data` is an ORM model.
        :type table: t.Optional[str]
        :param schema: The schema of the target table. If not provided, it is inferred from the ORM model if
            `data` is an ORM model.
        :type schema: t.Optional[str]
        :param on_conflict: A sequence of column names to resolve conflicts on. If specified, conflicts are
            resolved based on these columns.
        :type on_conflict: t.Optional[t.Sequence[str]]
        :param update_now_fields: A sequence of column names that should be updated with the current
            timestamp in conflict scenarios. Defaults to ("updated_at",).
        :type update_now_fields: t.Sequence[str]
        :param commit: Whether to commit the transaction immediately after executing the query. Defaults to
            True.
        :type commit: bool
        :return: Returns the inserted row as a dictionary or the updated ORM model if the data is an ORM
            model. If no data is returned, the result will be None.
        :rtype: MODEL_ORM_TYPE | t.Mapping[str, t.Any] | None
        """
        if not data:
            logger.warning("No data provided for insert operation.")
            raise ValueError("Data for insert operation cannot be empty.")

        is_orm_model = isinstance(data, BaseModelPostgreSQL)

        if is_orm_model:
            table_identifier = psycopg.sql.Identifier(data.__table__.schema, data.__tablename__) if data.__table__.schema else psycopg.sql.Identifier(data.__tablename__)
            columns = [column.key for column in data.__mapper__.columns if getattr(data, column.key, None) is not None]
            vars = {column: getattr(data, column, None) for column in columns}
        else:
            table_identifier = psycopg.sql.Identifier(schema, table) if schema else psycopg.sql.Identifier(table)
            columns = tuple(data.keys())
            vars = copy.deepcopy(data)

        insert = psycopg.sql.SQL("{insert} {table} ({fields}) {values} ({placeholders})").format(
            insert=SQLKeywordConst.PostgreSQL.INSERT_INTO,
            table=table_identifier,
            fields=psycopg.sql.SQL(", ").join(map(psycopg.sql.Identifier, columns)),
            values=SQLKeywordConst.PostgreSQL.VALUES,
            placeholders=psycopg.sql.SQL(", ").join(psycopg.sql.Placeholder(column) for column in columns),
        )

        conflict_clause = psycopg.sql.SQL("")
        if on_conflict:
            update_fields = [column for column in columns if column not in on_conflict]
            update_exprs: list[psycopg.sql.Composed] = []

            if not update_fields:
                update_exprs.append(psycopg.sql.SQL("{field} = now()").format(field=psycopg.sql.Identifier("updated_at")))
            else:
                for column in update_fields:
                    if column in update_now_fields:
                        update_exprs.append(psycopg.sql.SQL("{field} = now()").format(field=psycopg.sql.Identifier(column)))
                    else:
                        update_exprs.append(
                            psycopg.sql.SQL("{field} = {excluded}.{field}").format(
                                field=psycopg.sql.Identifier(column),
                                excluded=SQLKeywordConst.PostgreSQL.EXCLUDED,
                            )
                        )

            if update_exprs:
                conflict_clause = psycopg.sql.SQL("{on_conflict} ({conflict_fields}) {do} {updates}").format(
                    on_conflict=SQLKeywordConst.PostgreSQL.ON_CONFLICT,
                    conflict_fields=psycopg.sql.SQL(", ").join(map(psycopg.sql.Identifier, on_conflict)),
                    do=SQLKeywordConst.PostgreSQL.DO_UPDATE_SET,
                    updates=psycopg.sql.SQL(", ").join(update_exprs),
                )
            else:
                conflict_clause = psycopg.sql.SQL("{on_conflict} ({conflict_fields}) {do}").format(
                    on_conflict=SQLKeywordConst.PostgreSQL.ON_CONFLICT,
                    conflict_fields=psycopg.sql.SQL(", ").join(map(psycopg.sql.Identifier, on_conflict)),
                    do=SQLKeywordConst.PostgreSQL.DO_NOTHING,
                )

        query = psycopg.sql.SQL("{insert} {conflict} {returning} *;").format(
            insert=insert,
            conflict=conflict_clause,
            returning=SQLKeywordConst.PostgreSQL.RETURNING,
        )

        exec_query_lang = PostgreSQLExecuteStructure(query, vars)
        cursor = self.execute(exec_query_lang, commit=commit)
        row: t.Optional[t.Mapping[str, t.Any]] = cursor.fetchone()

        logger.debug(f"Inserted row: {row}")

        if is_orm_model and row is not None:
            for key, value in row.items():
                setattr(data, key, value)
            return data

        return row
