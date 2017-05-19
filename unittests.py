import os
import time
import unittest
from multiprocessing import Queue
from Queue import Empty as QueueEmpty

import MySQLdb

import mylogger
from db import MyDB
from net import Master


def test_function(test_queue):
    while True:
        try:
            arg = test_queue.get_nowait()
            if arg == 'END':
                break
        except QueueEmpty:
            time.sleep(0.5)
            continue
        print arg

test_logger = mylogger.mylogger()


class TestNet(unittest.TestCase):
    def setUp(self):
        self.master = Master(test_logger)

    def test_initial_wokers(self):
        self.assertEqual(len(self.master.workers), 0)
        self.assertEqual(len(self.master.order), 0)

    def test_add_worker(self):
        self.master.new_worker('test1', 3, test_function, (10,))
        self.master.new_worker('test2', 3, test_function, (10,))
        self.master.new_worker('test3', 3, test_function, (10,))
        self.assertEqual(len(self.master.workers), 3)
        self.assertEqual(len(self.master.order), 3)

    # def test_run_master(self):
    #     test_queue = Queue(20)
    #     for i in range(15):
    #         test_queue.put(5)
    #     self.master.new_worker('test1', 3, test_function, (test_queue,))
    #     self.master.new_worker('test2', 3, test_function, (test_queue,))
    #     self.master.new_worker('test3', 3, test_function, (test_queue,))
        # self.master.start()
        # self.master.shutdown()

    def tearDown(self):
        self.master = None


create_sql = '''
CREATE TABLE unittest (
    `id` SERIAL
    , `field1` varchar(60)
    , `field2` int
    , `field3` datetime
)
'''


class TestDB(unittest.TestCase):
    def setUp(self):
        self.sqlite_db = MyDB('test')
        self.mysql_db = MyDB('test', flavor='mysql')
        self.mysql_db.curs.execute(create_sql)

    def test_create_sqlite(self):
        self.assertTrue(os.path.exists('test.db'))

    def test_mysql_create_db(self):
        self.mysql_db.curs.execute('show databases')
        databases = [x[0] for x in self.mysql_db.curs.fetchall()]
        self.assertTrue('test' in databases)

    def test_mysql_create_tables(self):
        self.mysql_db.curs.execute('use test')
        self.mysql_db.curs.execute('show tables')
        tables = [x[0] for x in self.mysql_db.curs.fetchall()]
        self.assertTrue('geo' in tables)
        self.assertTrue('rdap' in tables)

    def test_construct_insert_query(self):
        sql, cols = self.mysql_db.construct_insert_query('unittest')
        insert, duplicate = sql
        self.assertEquals(cols, ['id', 'field1', 'field2', 'field3'])
        self.assertEquals(insert, 'INSERT INTO unittest (id,field1,field2,field3) VALUES ')
        self.assertEquals(duplicate, 'ON DUPLICATE KEY UPDATE field1 = VALUES(field1), field2 = VALUES(field2), field3 = VALUES(field3)')

    def test_query_to_string(self):
        sql, cols = self.mysql_db.construct_insert_query('unittest')
        queries = [(1, 'asdf', 60, '2017/05/04 15:34'), (2, 'merp', 28, '1988/11/11 20:10')]
        string = self.mysql_db.query_to_string('unittest', queries)
        self.assertEquals(string, '''(1,"asdf",60,'2017-05-04 15:34:00'),(2,"merp",28,'1988-11-11 20:10:00')''')

    def test_multi_insert(self):
        sql, cols = self.mysql_db.construct_insert_query('unittest')
        queries = [(1, 'asdf', 60, '2017/05/04 15:34'), (2, 'merp', 28, '1988/11/11 20:10')]
        try:
            self.mysql_db.multi_insert('unittest', sql, queries)
        except:
            self.fail

    def tearDown(self):
        os.remove('test.db')
        self.sqlite_db.curs.close()
        self.sqlite_db.curs.close()
        self.mysql_db.curs.execute('drop database test')
        self.mysql_db.curs.close()
        self.mysql_db.conn.close()


if __name__ == '__main__':
    unittest.main()
