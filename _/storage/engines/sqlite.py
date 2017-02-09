
import logging
import os

import _

from . import Storage

try:
    import sqlite3
except ImportError:
    raise _.error('Missing sqlite3 module')


class Sqlite(Storage):
    def __init__(self, path=None, schema=None):
        if path is None:
            path = ':memory:'

        try:
            self.conn = sqlite3.connect(path)
        except sqlite3.OperationalError:
            raise _.error('Unable to open database: %s', path)

        self.conn.text_factory = str
        self.conn.row_factory  = sqlite3.Row

        self.cursor = self.conn.cursor()

        if schema and not os.path.isfile(path):
            if not os.path.isfile(schema):
                schema = _.paths('etc', schema)

            if os.path.isfile(schema):
                logging.debug('Attempt to load schema: %s', schema)
                schema = open(schema, 'rb').read()
                self.cursor.executescript(schema)
                self.conn.commit()
            else:
                raise _.error('Schema not found: %s', schema)

    def Cursor(self):
        return self.conn.cursor()

    def Close(self):
        self.conn.commit()
        self.conn.close()

    def Sync(self):
        self.conn.commit()

    def Find(self, table, params=None, sort=None):
        statement = 'SELECT * FROM ' + table
        if params:
            statement += ' WHERE ' + params
        if sort:
            statement += ' ' + sort

        self.cursor.execute(statement)
        return self.cursor.fetchall()

    def FindOne(self, table, _id, id_column='id'):
        statement = 'SELECT * FROM {0} WHERE {1} = ?'.format(table, id_column)
        self.cursor.execute(statement, [_id])
        return self.cursor.fetchone()

    def Count(self, table):
        statement = 'SELECT count(*) FROM {0}'.format(table)
        self.cursor.execute(statement)
        return self.cursor.fetchone()[0]

    def Insert(self, table, values, id_column='id'):
        columns = ','.join(values.keys())
        placeholder = ','.join('?' * len(values))
        statement = 'INSERT INTO {0} ({1}) VALUES ({2})'.format(table, columns, placeholder)

        try:
            self.cursor.execute(statement, values.values())
        except sqlite3.ProgrammingError as e:
            raise pyaas.error('Problem executing statement: %s', e)
        except sqlite3.IntegrityError as e:
            raise pyaas.error('Integrity error: %s', e)

        if id_column not in values:
            values[id_column] = self.cursor.lastrowid

    def Update(self, table, values, id_column='id'):
        _id = values[id_column]
        columns = ','.join(s + '=?' for s in values.keys())
        statement = 'UPDATE {0} SET {1} WHERE id=?'.format(table, columns, _id)
        try:
            self.cursor.execute(statement, values.values() + [_id])
        except sqlite3.ProgrammingError:
            raise pyaas.error('Problem executing statement')

    def Remove(self, table, _id, id_column='id'):
        statement = 'DELETE FROM {0} WHERE {1} = ?'.format(table, id_column)
        self.cursor.execute(statement, [_id])
