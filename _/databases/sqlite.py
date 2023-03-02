#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import logging
import os
import sqlite3

import _

try:
    import aiosqlite
except ImportError:
    raise _.error('Missing aiosqlite module')

logging.getLogger("aiosqlite").setLevel(logging.WARNING)


class SQLite(_.databases.Database):
    async def init(self, path=None, schema=None):
        try:
            self.conn = await aiosqlite.connect(path)
        except sqlite3.OperationalError:
            raise _.error('Unable to open database: %s', path)

        self.conn.row_factory = sqlite3.Row

        cursor = await self.conn.cursor()
        await cursor.execute('PRAGMA foreign_keys = ON;')
        await cursor.close()

        if not os.path.isfile(schema):
            schema = _.paths(schema)

        if os.path.isfile(schema):
            logging.info('Loading schema: %s', schema)
            schema = open(schema, 'r').read()
            cursor = await self.conn.cursor()
            await cursor.executescript(schema)
            await self.conn.commit()
        else:
            raise _.error('Schema not found: %s', schema)

    async def close(self):
        await self.conn.commit()
        await self.conn.close()

    async def execute(self, statement, args):
        cursor = await self.conn.cursor()
        try:
            await cursor.execute(statement, args)
        except sqlite3.OperationalError as e:
            raise _.error('Operational error: %s', e)
        except sqlite3.ProgrammingError as e:
            raise _.error('Programming error: %s', e)
        except sqlite3.IntegrityError as e:
            raise _.error('Integrity error: %s', e)
        finally:
            await cursor.close()
        await self.conn.commit()

    async def find(self, table, params=None, sort=None):
        statement = f'SELECT * FROM {table}'
        if params:
            statement += ' WHERE ' + params
        if sort:
            statement += ' ' + sort

        cursor = await self.conn.cursor()
        await cursor.execute(statement)
        rows = await cursor.fetchall()
        await cursor.close()
        return rows

    async def find_one(self, table, value, column='id'):
        statement = f'SELECT * FROM {table} WHERE {column}=? LIMIT 1'

        try:
            cursor = await self.conn.cursor()
            await cursor.execute(statement, (value,))
        except sqlite3.OperationalError as e:
            raise _.error('%s', e)
        row = await cursor.fetchone()
        await cursor.close()
        return dict(row) if row else None

    async def count(self, table):
        statement = f'SELECT count(*) FROM {table}'

        try:
            cursor = await self.conn.cursor()
            await cursor.execute(statement)
            return cursor.fetchone()[0]
        except sqlite3.ProgrammingError as e:
            raise _.error('Problem executing statement: %s', e)
        except sqlite3.IntegrityError as e:
            raise _.error('Integrity error: %s', e)
        finally:
            await cursor.close()

    async def insert(self, table, values, id_column='id'):
        columns = ','.join(f'"{s}"' for s in values.keys())
        placeholder = ','.join('?' * len(values))
        statement = f'INSERT INTO {table} ({columns}) VALUES ({placeholder})'
        await self.execute(statement, list(values.values()) + [where])
        if id_column not in values:
            values[id_column] = cursor.lastrowid

    async def update(self, table, values, column='id'):
        where = values.get(column)
        columns = ','.join(f'{s}=?' for s in values.keys())
        statement = f'UPDATE {table} SET {columns} WHERE {column}=?'
        await self.execute(statement, list(values.values()) + [where])

    async def upsert(self, table, values):
        columns = ','.join(f'"{s}"' for s in values.keys())
        placeholder = ','.join('?' * len(values))
        statement = f'INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholder})'
        await self.execute(statement, list(values.values()))

    async def delete(self, table, value, column='id'):
        statement = f'DELETE FROM {table} WHERE {column}=?'
        await self.execute(statement, (value,))
