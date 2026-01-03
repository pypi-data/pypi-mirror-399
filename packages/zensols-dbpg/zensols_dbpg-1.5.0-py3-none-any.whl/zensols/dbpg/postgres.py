"""Postgres implementation of the ``ConnectionManager``.

"""
__author__ = 'Paul Landes'

from typing import Any, Tuple, Union, Callable
from dataclasses import dataclass, field
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import ProgrammingError
import pandas as pd
from zensols.db import DBError, ConnectionManager

logger = logging.getLogger(__name__)


@dataclass
class PostgresConnectionManager(ConnectionManager):
    """An Postgres connection factory.

    """
    EXISTS_SQL = 'select count(*) from information_schema.tables where table_schema = \'public\''
    DROP_SQL = 'drop owned by {user}'

    db_name: str = field()
    """Database name on the server."""

    host: str = field()
    """The host name of the database."""

    port: str = field()
    """The host port of the database."""

    user: str = field()
    """The user (if any) to log in with."""

    password: str = field()
    """The login password."""

    create_db: bool = field(default=True)
    """If ``True`` create the database if it does not already exist."""

    capture_lastrowid: bool = field(default=False)
    """If ``True``, select the last row for each query."""

    fast_insert: bool = field(default=False)
    """If ``True`` use `insertmany` on the cursor for fast insert in to the
    database.

    """
    def _init_db(self, conn, cur):
        if logger.isEnabledFor(logging.DEBUG):
            logger.info('initializing database...')
        for sql in self.persister.parser.get_init_db_sqls():
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'invoking sql: {sql}')
            cur.execute(sql)
            conn.commit()

    def create(self):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'creating connection to {self.host}:{self.port} ' +
                         f'with {self.user} on database: {self.db_name}')
        conn = psycopg2.connect(
            host=self.host, database=self.db_name, port=self.port,
            user=self.user, password=self.password)
        try:
            cur = conn.cursor()
            cur.execute(self.EXISTS_SQL, ())
            if cur.fetchone()[0] == 0:
                self._init_db(conn, cur)
        finally:
            cur.close()
        return conn

    def drop(self):
        conn = self.create()
        cur = conn.cursor()
        try:
            cur.execute(self.DROP_SQL.format(**self.__dict__))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def execute(self, conn: Any, sql: str, params: Tuple[Any],
                row_factory: Union[str, Callable],
                map_fn: Callable) -> Tuple[Union[dict, tuple, pd.DataFrame]]:
        """See :meth:`~zensols.db.bean.ConnectionManager.execute`.

        """
        def other_rf_fn(row):
            return row_factory(*row)

        def identity_rf_fn(row):
            return row

        create_fn = None
        if row_factory == 'dict':
            cur = conn.cursor(cursor_factory=RealDictCursor)
        elif row_factory == 'tuple' or row_factory == 'pandas':
            cur = conn.cursor()
        elif row_factory == 'identity':
            create_fn = identity_rf_fn
            cur = conn.cursor()
        else:
            create_fn = other_rf_fn
            cur = conn.cursor()
        try:
            tupify = True
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'pg exec sql=<{sql}>, params=<{params}>')
            cur.execute(sql, params)
            res = cur.fetchall()
            if create_fn is not None:
                res = map(create_fn, res)
            if map_fn is not None:
                res = map(map_fn, res)
            if row_factory == 'pandas':
                res = self._to_dataframe(res, cur)
                tupify = False
            if tupify:
                res = tuple(res)
            return res
        finally:
            cur.close()

    def execute_no_read(self, conn, sql, params=()) -> int:
        cur = conn.cursor()
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'execute no read: {sql}')
        try:
            cur.execute(sql, params)
            conn.commit()
            if self.capture_lastrowid is not None:
                try:
                    return cur.fetchone()[0]
                except ProgrammingError:
                    # actions like dropping a table will not return a rowid
                    pass
        finally:
            cur.close()

    def _insert_row(self, conn, cur, sql, row):
        cur.execute(sql, row)
        conn.commit()
        if self.capture_lastrowid:
            return cur.fetchall()[0][0]

    def _insert_rows_slow(self, conn, sql, rows: list, errors: str,
                          set_id_fn, map_fn) -> int:
        rowid = None
        cur = conn.cursor()
        try:
            for row in rows:
                if map_fn is not None:
                    org_row = row
                    row = map_fn(row)
                if errors == 'raise':
                    rowid = self._insert_row(conn, cur, sql, row)
                elif errors == 'ignore':
                    try:
                        rowid = self._insert_row(conn, cur, sql, row)
                    except Exception as e:
                        logger.error(f'could not insert row ({len(row)})', e)
                else:
                    raise DBError(f'Unknown errors value: {errors}')
                if set_id_fn is not None:
                    set_id_fn(org_row, cur.lastrowid)
        finally:
            cur.close()
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'inserted with rowid: {rowid}')
        return rowid

    def _insert_rows_fast(self, conn, sql, rows: list, map_fn) -> int:
        cur = conn.cursor()
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('inserting rows fast')
        try:
            if map_fn is not None:
                rows = map(map_fn, rows)
            cur.executemany(sql, rows)
            conn.commit()
        finally:
            cur.close()

    def insert_rows(self, conn, sql, rows: list, errors: str,
                    set_id_fn, map_fn) -> int:
        if self.fast_insert:
            return self._insert_rows_fast(conn, sql, rows, map_fn)
        else:
            return self._insert_rows_slow(
                conn, sql, rows, errors, set_id_fn, map_fn)
