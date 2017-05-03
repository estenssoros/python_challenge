import json
import os
import sqlite3
import sys
import warnings

from dateutil import parser

import sql_statements

try:
    import MySQLdb
except ImportError:
    warnings.warn('MySQLdb not found. Will default to sqlite3')


class MyDB(object):
    def __init__(self, dbname, flavor='sqlite3', mysql_params=None):
        self.dbname = dbname
        self.flavor = flavor  # TODO: mysql, mongod
        self.conn, self.curs = self.create_db()
        self.descriptions = {}

    def create_db(self):
        '''
        router to return db conn and cursor objects
        '''
        if self.flavor == 'sqlite3':
            warnings.warn('django app only supports mysql')
            return self.create_sqlite_db()
        if self.flavor == 'mysql':
            return self.create_mysql_db()

    def create_sqlite_db(self):
        '''
        creates sqlite database and associated tables
        '''
        if not self.dbname.endswith('.db'):
            self.dbname += '.db'
        if os.path.exists(self.dbname):
            os.remove(self.dbname)
        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql_statements.CREATE_GEO_TABLE)
        curs.execute(sql_statements.CREATE_RDAP_TABLE)
        return conn, curs

    def create_mysql_db(self):
        '''
        creates mysql database and associated tables
        '''
        if 'MySQLdb' not in sys.modules:
            warnings.warn('MySQLdb not found defaulting to sqlite3')
            return self.create_sqlite_db()
        conn = MySQLdb.connect()
        curs = conn.cursor()
        curs.execute(sql_statements.MYSQL_SUPRESS_WARN)
        curs.execute('SHOW DATABASES')
        dbs = [x[0] for x in curs.fetchall()]
        if self.dbname not in dbs:
            print 'creating database'
            curs.execute(sql_statements.MYSQL_CREATE_DB)
        curs.execute('''use {}'''.format(self.dbname))
        curs.execute('SHOW TABLES')
        tbls = [x[0] for x in curs.fetchall()]
        if 'geo' not in tbls:
            curs.execute(sql_statements.CREATE_GEO_TABLE)

        if 'rdap' not in tbls:
            curs.execute(sql_statements.CREATE_RDAP_TABLE)
        curs.execute(sql_statements.DROP_TF)
        curs.execute(sql_statements.CREATE_TF)
        return conn, curs

    def construct_insert_query(self, table_name):
        '''
        INPUT: cursor object, table name
        OUTPUT: sql statement for inserting into all columns of table along with
        list of fields in table
        '''
        insert_part = '''INSERT INTO {} ('''.format(table_name)
        self.curs.execute('select * from %s limit 1' % table_name)
        self.descriptions[table_name] = self.curs.description
        cols = [x[0] for x in self.descriptions[table_name]]
        insert_part = insert_part + ','.join(cols) + ') VALUES '
        duplicate_part = 'ON DUPLICATE KEY UPDATE '
        duplicate_part += ', '.join(['{0} = VALUES({0})'.format(x) for x in cols[1:]])
        return (insert_part, duplicate_part), cols

    def query_to_string(self, table_name, queries):
        '''
        converts list of queries lists into string for mysql multi insert
        '''
        desc = self.descriptions[table_name]
        string_fields = []
        datetime_fields = []
        other_fields = []
        for i in range(len(desc)):
            if desc[i][1] in MySQLdb.STRING or desc[i][1] == MySQLdb.FIELD_TYPE.BLOB:
                string_fields.append(i)
            elif desc[i][1] in MySQLdb.DATETIME:
                datetime_fields.append(i)
            else:
                other_fields.append(i)
        values = []
        for row in queries:
            row = list(row)
            for idx in string_fields:
                row[idx] = '"{}"'.format(MySQLdb.escape_string(row[idx].encode('utf-8'))) if row[idx] else 'NULL'
            for idx in datetime_fields:
                row[idx] = parser.parse(row[idx]).strftime("'%Y-%m-%d %H:%M:%S'") if row[idx] else 'NULL'
            for idx in other_fields:
                row[idx] = str(row[idx]) if row[idx] is not None else 'NULL'
            values.append('(' + ','.join(row) + ')')
        return ','.join(values).replace('%', '%%')

    def multi_insert(self, table_name, sql, queries):
        '''
        insert multiple rows at once
        '''
        insert_part, duplicate_part = sql
        queries = self.query_to_string(table_name, queries)
        self.curs.execute(insert_part + queries + duplicate_part)
        self.conn.commit()
