import threading
import logging
from utils import Dict
import mysql.connector

# global connector function:
connector = None


class DateBaseError(Exception):
    pass


class MultiColumnsError(DateBaseError):
    pass


class _LazyConnection(object):
    """
    Database connection object.

    Lazy Connect the Database when function cursor is called.
    """

    def __init__(self):
        self._connection = None

    def cursor(self):
        """Return cursor"""
        global connector
        if self._connection is None:
            if connector is None:
                raise DateBaseError('Connector is not initialized.')
            self._connection = connector()
            logging.info('open connection <%s>...' % hex(id(self._connection)))
        return self._connection.cursor()

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def cleanup(self):
        if self._connection:
            connection = self._connection
            self._connection = None
            logging.info('close connection <%s>...' % hex(id(connection)))
            connection.close()


class _DbContext(threading.local):
    """Thread local object that holds connection info."""

    def __init__(self):
        self.connection = None
        self.transactions = 0

    def init(self):
        """
        init the connection.

        :return is new connection created
        :rtype bool
        """
        is_init = self.connection is not None
        if not is_init:
            logging.info('open lazy connection...')
            self.connection = _LazyConnection()
            self.transactions = 0
        return not is_init

    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    def cursor(self):
        return self.connection.cursor()


# global db context object:
db_context = _DbContext()


def init_engine(user, password, database, host='127.0.0.1', port=3306, **kw):
    global connector
    if connector is not None:
        raise DateBaseError('Connector is already initialized.')
    params = dict(user=user, password=password, database=database, host=host, port=port)
    defaults = dict(use_unicode=True, charset='utf8', collation='utf8_general_ci', autocommit=False, buffered=True)
    for k, v in defaults.items():
        params[k] = kw.pop(k, v)
    params.update(kw)
    connector = lambda: mysql.connector.connect(**params)
    logging.info('Init mysql engine <%s> ok.' % hex(id(connector)))


def close_engine():
    global connector
    connector = None


class _ConnectionContext(object):
    """
    Connection Context object that can open and close connection context. The object can be nested and only the most
    outer connection has effect.
    with connection():
        pass
        with connection():
            pass
    """

    def __enter__(self):
        global db_context
        self.should_cleanup = db_context.init()
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global db_context
        if self.should_cleanup:
            db_context.cleanup()


def with_connection(func):
    """Decorator for reuse connection."""

    def wrapper(*args, **kw):
        with _ConnectionContext():
            return func(*args, **kw)

    return wrapper


class TransactionContext(object):
    """Transaction context object which handle the transactions"""

    def __enter__(self):
        global db_context
        self.should_close_connection = db_context.init()
        db_context.transactions += 1
        logging.info('begin transaction...' if db_context.transactions == 1 else 'join current transaction...')
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global db_context
        db_context.transactions -= 1
        try:
            if db_context.transactions == 0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_connection:
                db_context.cleanup()

    def commit(self):
        global db_context
        logging.info('commit transaction...')
        try:
            db_context.connection.commit()
            logging.info('commit ok.')
        except:
            logging.warning('commit failed. try rollback...')
            db_context.connection.rollback()
            logging.warning('rollback ok.')
            raise

    def rollback(self):
        global db_context
        logging.warning('rollback transaction...')
        db_context.connection.rollback()
        logging.info('rollback ok.')


def with_transaction(func):
    """A decorator that makes function around transaction."""

    def wrapper(*args, **kw):
        with TransactionContext():
            return func(*args, **kw)

    return wrapper


def base_select(sql, single, *args):
    """execute select SQL and fetch results."""
    global db_context
    cursor = None
    sql = sql.replace('?', '%s')
    logging.info('SQL: %s, ARGS: %s' % (sql, args))
    try:
        cursor = db_context.connection.cursor()
        cursor.execute(sql, args)
        if cursor.description:
            names = [x[0] for x in cursor.description]
        else:
            raise DateBaseError("No cursor description.")
        if single:
            values = cursor.fetchone()
            if not values:
                return None
            return Dict(names, values)
        return [Dict(names, x) for x in cursor.fetchall()]
    finally:
        if cursor:
            cursor.close()


@with_connection
def select_one(sql, *args):
    """Execute insert SQL and fetch the first result"""
    return base_select(sql, True, *args)


@with_connection
def select_int(sql, *args):
    """Execute insert SQL with integer result"""
    d = base_select(sql, True, *args)
    if len(d) != 1:
        raise MultiColumnsError('Expect only one column.')
    return d.values()[0]


@with_connection
def select(sql, *args):
    """Execute select SQL"""
    return base_select(sql, False, *args)


@with_connection
def base_update(sql, *args):
    global db_context
    cursor = None
    sql = sql.replace('?', '%s')
    logging.info('SQL: %s, ARGS: %s' % (sql, args))
    try:
        cursor = db_context.connection.cursor()
        cursor.execute(sql, args)
        r = cursor.rowcount
        # No transaction:
        if db_context.transactions == 0:
            logging.info('auto commit')
            db_context.connection.commit()
        return r
    finally:
        if cursor:
            cursor.close()


@with_connection
def multi_base_update(sql, *args):
    global db_context
    cursor = None
    sql = sql.replace('?', '%s')
    logging.info('SQL: %s, ARGS: %s' % (sql, args))
    try:
        cursor = db_context.connection.cursor()
        cursor.execute(sql, args, multi=True)
        r = cursor.rowcount
        # No transaction:
        if db_context.transactions == 0:
            logging.info('auto commit')
            db_context.connection.commit()
        return r
    finally:
        if cursor:
            cursor.close()


def insert(table, **kw):
    """Execute insert SQL"""
    cols, args = zip(*kw.items())
    sql = 'insert into `%s` (%s) values (%s)' % (
        table, ','.join(['`%s`' % col for col in cols]), ','.join(['?' for _ in range(len(cols))]))
    return base_update(sql, *args)


def update(sql, *args):
    """Execute update SQL"""
    return base_update(sql, *args)


# TODO  fix bug
def multi_update(sql, *args):
    """Execute multi update SQL"""
    return multi_base_update(sql, *args)
