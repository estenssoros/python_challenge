# coding: utf-8
from __future__ import division

import random
import threading
import time
from multiprocessing import Process, Queue, cpu_count
from Queue import Empty as QueueEmpty

import pandas as pd
import requests

import mylogger
from db import MyDB
from net import Master
from utils import MyUtil


class Interview(object):
    '''
    Strengths: willingness to sacrifice my personal life for work.
    Weakness: poorly timed sense for jokes.
    '''

    def __init__(self):
        self.geo_url = 'http://freegeoip.net/json/%s'
        self.rdap_url = 'http://rdap.arin.net/bootstrap/ip/%s'
        self.dbname = 'swimlane'
        self.timeout_limit = 10
        self.NUMBER_OF_READERS = 3
        self.NUMBER_OF_WRITERS = 2
        self.NUMBER_OF_REPORTERS = 1
        self.logger = mylogger.mylogger()

    def query_api(self, url, ip_address, results, timeouts=0):
        '''
        query either geo or rdap api
        '''
        if timeouts == self.timeout_limit:
            return None
        try:
            resp = requests.get(url % ip_address, timeout=1).json()
            resp['ip'] = ip_address
            if 'rdap' in url:
                resp = self.my_util.parse_rdap_json(resp)
            results.append(resp)
            self.logger.info('success: {}'.format(url) % ip_address)
        except Exception as e:
            self.logger.debug('error: {} - retrying {}/{}...'.format(url, timeouts, self.timeout_limit) % ip_address)
            time.sleep(2)
            self.query_api(url, ip_address, results, timeouts=timeouts + 1)

    def ip_queue_thread_handler(self, ip_queue, write_queue):
        NUMBER_OF_THREADS = 10
        worklist = []
        while True:
            try:
                arg = ip_queue.get_nowait()
                if arg == 'END':
                    break
            except QueueEmpty:
                time.sleep(1.5)
                continue
            worklist.append(arg)
            if len(worklist) == NUMBER_OF_THREADS:
                threads = []
                results = []
                for ip, url in worklist:
                    thread = threading.Thread(target=self.query_api, args=(url, ip, results))
                    threads.append(thread)
                    thread.start()
                for thread in threads:
                    thread.join()
                for resp in results:
                    write_queue.put(resp)
                worklist = []

    def db_writer(self, write_queue, reporter_queue, table_name):
        query_limit = 100
        sql, cols = self.my_db.construct_insert_query(table_name)
        end_count = 0
        queries = []

        while True:
            try:
                item = write_queue.get_nowait()
                if item == 'END':
                    break
                else:
                    queries.append([item[x] for x in cols])
            except QueueEmpty:
                time.sleep(1)

            if len(queries) == query_limit:
                self.my_db.multi_insert(table_name, sql, queries)
                reporter_queue.put(query_limit)
                queries = []

        if queries:
            self.my_db.multi_insert(table_name, sql, queries)
            reporter_queue.put(len(queries))

    def simple_reporter(self, reporter_queue, ttl):
        count = 0
        t1 = time.time() + 15.0
        while True:
            try:
                item = reporter_queue.get_nowait()
                if item == 'END':
                    break
                count += item
            except QueueEmpty:
                time.sleep(1)
                continue
            if time.time() > t1:
                self.logger.info('progress: {0}/{1} - {2:.2f}%'.format(count, ttl, (count / ttl * 100)))
                t1 == time.time() + 15.0

    def get_ip_data(self, ips):
        self.my_db = MyDB(self.dbname, flavor='mysql')
        self.my_util = MyUtil()
        self.master = Master(self.logger)

        geo_ip_queue = Queue(len(ips) * 3)
        rdap_ip_queue = Queue(len(ips) * 3)
        geo_write_queue = Queue(len(ips) * 3)
        rdap_write_queue = Queue(len(ips) * 3)
        reporter_queue = Queue(len(ips) * 3)

        self.master.new_worker('rdap reader', self.NUMBER_OF_READERS, self.ip_queue_thread_handler, (rdap_ip_queue, rdap_write_queue))
        self.master.new_worker('rdap writer', self.NUMBER_OF_WRITERS, self.db_writer, (rdap_write_queue, reporter_queue, 'rdap'))
        self.master.new_worker('geo reader', self.NUMBER_OF_READERS, self.ip_queue_thread_handler, (geo_ip_queue, geo_write_queue))
        self.master.new_worker('geo writer', self.NUMBER_OF_WRITERS, self.db_writer, (geo_write_queue, reporter_queue, 'geo'))
        self.master.new_worker('simple reporter', self.NUMBER_OF_REPORTERS, self.simple_reporter, (reporter_queue, len(ips) * 2))

        self.master.start()

        for ip in ips:
            rdap_ip_queue.put((ip, self.rdap_url))
            geo_ip_queue.put((ip, self.geo_url))

        self.master.shutdown()


if __name__ == '__main__':
    interview = Interview()
    my_util = MyUtil()
    ips = my_util.extract_ips('list_of_ips.txt')
    interview.get_ip_data(ips[:50])
