
import logging
import re

import tornado.ioloop
import tornado.gen

import _.storage

from . import Storage

try:
    import psycopg2
    import psycopg2.extensions
    import psycopg2.extras
except ImportError:
    raise _.error('Missing psycopg2 (PostgreSQL) module')

try:
    import momoko
except ImportError:
    raise _.error('Missing momoko (PostgreSQL) module')

psycopg2.extensions.string_types.pop(psycopg2.extensions.JSON.values[0],      None)
psycopg2.extensions.string_types.pop(psycopg2.extensions.JSONARRAY.values[0], None)

psycopg2.extras.register_uuid()

# Squelch debug messages
momoko_log = logging.getLogger('momoko')
momoko_log.setLevel(logging.INFO)


class Postgres(Storage):
    def __init__(self, **kwds):
        dsn = ' '.join('{0}={1}'.format(k, v) for k,v in kwds.items())

        sanitized = re.sub('password=[^ ]*', 'password=****', dsn)
        logging.info('DSN: %s', sanitized)

        ioloop = tornado.ioloop.IOLoop.instance()

        self.db = momoko.Pool(
            dsn        = dsn,
            size       = 5,
            max_size   = 10,
            setsession = ("SET TIME ZONE UTC",),
            ioloop     = ioloop,
            cursor_factory = psycopg2.extras.DictCursor,
            raise_connect_errors = True,
            )

        future = self.db.connect()
        ioloop.add_future(future, lambda f: ioloop.stop())
        ioloop.start()
        try:
            future.result()
        except Exception as e:
            raise _.error('Connection error: %s', e)

    def Sync(self, statement, *args):
        ioloop = tornado.ioloop.IOLoop.instance()

        future = self.db.execute(statement, args)
        ioloop.add_future(future, lambda f: ioloop.stop())
        ioloop.start()
        cursor = future.result()
        return cursor

    @tornado.gen.coroutine
    def Exec(self, statement, *args):
        cursor = yield self.db.execute(statement, args)
        raise tornado.gen.Return(cursor)


#    def Sync(self, fn, *args, **kwds):
#        @tornado.gen.coroutine
#        def _Sync():
#            cursor = yield fn(*args, **kwds)
#            raise tornado.gen.Return(cursor)
#        try:
#            res = tornado.ioloop.IOLoop.current().run_sync(_Sync)
#        except Exception as e:
#            logging.exception('Postgres')
#            raise _.error('%s', e)
#        return res

#    @tornado.gen.coroutine
#    def Execute(self, statement, *args):
#        cursor = yield self.db.execute(statement, args)
#        raise tornado.gen.Return(cursor)
#
#    @tornado.gen.coroutine
#    def FindOne(self, table, _id, id_column='id'):
#        statement = 'SELECT * FROM {0} WHERE {1} = %s'.format(table, id_column)
#        cursor = yield self.db.execute(statement, [_id])
#        raise tornado.gen.Return(cursor.fetchone())
#
#    @tornado.gen.coroutine
#    def Insert(self, table, values, id_column='id'):
#        columns = ','.join('"%s"' % k.lower() for k in values.keys())
#        placeholder = ','.join('%s' for x in xrange(len(values)))
#        statement = 'INSERT INTO {0} ({1}) VALUES ({2})'.format(table, columns, placeholder)
#
#        cursor = yield self.db.execute(statement, values.values())
#
#        rows = cursor.rowcount
#        if rows is None:
#            rows = -1
#
#        if id_column not in values:
#            cursor = yield self.db.execute('SELECT lastval()')
#            values[id_column] = cursor.fetchone()[0]
#
#        raise tornado.gen.Return(rows)
#
#    @tornado.gen.coroutine
#    def Update(self, table, values, id_column='id'):
#        _id = values[id_column]
#        columns = ','.join('"%s"=%%s' % s.lower() for s in values.keys())
#        statement = 'UPDATE {0} SET {1} WHERE {2}=%s'.format(table, columns, id_column)
#
#        cursor = yield self.db.execute(statement, values.values() + [_id])
#
#        rows = cursor.rowcount
#        if rows is None:
#            rows = -1
#
#        raise tornado.gen.Return(rows)
#
#    @tornado.gen.coroutine
#    def Upsert(self, table, values, id_column='id'):
#        rows = yield self.InsertUnique(table, values, id_column)
#        if rows <= 0:
#            rows = yield self.Update(table, values, id_column)
#        raise tornado.gen.Return(rows)
#
#    @tornado.gen.coroutine
#    def InsertUnique(self, table, values, id_column='id'):
#        columns = ','.join('"%s"' % k.lower() for k in values.keys())
#        placeholder = ','.join('%s' for x in xrange(len(values)))
#        statement = "INSERT INTO {0} ({1}) SELECT {2} WHERE NOT EXISTS (select {4} from {0} where {4} = '{3}')" \
#            .format(table, columns, placeholder, values[id_column], id_column)
#
#        cursor = yield self.db.execute(statement, values.values())
#
#        rows = cursor.rowcount
#        if rows is None:
#            rows = -1
#
#        raise tornado.gen.Return(rows)
