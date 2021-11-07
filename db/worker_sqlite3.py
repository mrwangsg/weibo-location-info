#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/30 16:27
# @Author  : sgwang
# @File    : worker_sqlite3.py
# @Software: PyCharm
import logging
import queue
import sqlite3
import threading
import time
import uuid

DEFAULT_LOGGER = logging.getLogger('sqlite3worker')


class Sqlite3Worker(threading.Thread):
    """Sqlite thread safe object.
        单线程执行sql语句，sql待执行放入线程安全的queue里
    Example:
        from sqlite3worker import Sqlite3Worker
        sql_worker = Sqlite3Worker("/tmp/test.sqlite")

        sql_worker.execute("CREATE TABLE tester (timestamp DATETIME, uuid TEXT)")
        sql_worker.execute("INSERT into tester values (?, ?)", ("2010-01-01 13:00:00", "bow"))
        sql_worker.execute("INSERT into tester values (?, ?)", ("2011-02-02 14:14:14", "dog"))
        sql_worker.execute("SELECT * from tester")

        sql_worker.close()

        :return 查询返回：{"code": "0", "status": True, "rows": rows, "err": None}
        :return 增删改返回：{"code": "0", "status": True, "rows": None, "err": None}
        :return 异常回滚 ：{"code": "-1", "status": False, "rows": None, "err": err}
    """

    def __init__(self, file_name, max_queue_size=100, logger=None):
        """Automatically starts the thread.

        Args:
            file_name: The name of the file.
            max_queue_size: The max queries that will be queued.
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.thread_running = True

        # 创建数据库连接
        self.sqlite3_conn = sqlite3.connect(file_name, check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
        self.sqlite3_cursor = self.sqlite3_conn.cursor()
        self.results = {}

        # 最大连接数设置
        self.max_queue_size = max_queue_size
        self.sql_queue = queue.Queue(maxsize=max_queue_size)

        # 日志打印设置
        self.LOGGER = DEFAULT_LOGGER if logger is None else logger

        # Token that is put into queue when close() is called.
        self.exit_set = False
        self.exit_token = str(uuid.uuid4())

        # 启动容器
        self.start()

    def run(self):
        """Thread loop.

        This is an infinite loop.  The iter method calls self.sql_queue.get()
        which blocks if there are not values in the queue.  As soon as values
        are placed into the queue the process will continue.

        If many executes happen at once it will churn through them all before
        calling commit() to speed things up by reducing the number of times
        commit is called.
        """
        self.LOGGER.debug("run: Thread started")

        for token, query, values in iter(self.sql_queue.get, None):
            self.LOGGER.debug("sql_queue: %s", self.sql_queue.qsize())

            if token != self.exit_token:
                self.LOGGER.debug("run: %s", query)

                run_flag = self.run_query(token, query, values)
                if run_flag:
                    self.sqlite3_conn.commit()
                else:
                    self.sqlite3_conn.rollback()

            # Only exit if the queue is empty. Otherwise keep getting
            # through the queue until it's empty.
            if self.exit_set and self.sql_queue.empty():
                self.sqlite3_conn.commit()
                self.sqlite3_conn.close()
                self.thread_running = False
                return

    def run_query(self, token, query, values):
        """Run a query.

        Args:
            token: A uuid object of the query you want returned.
            query: A sql query with ? placeholders for values.
            values: A tuple of values to replace "?" in query.
        """
        try:
            self.sqlite3_cursor.execute(query, values)

            if query.lower().strip().startswith("select"):
                rows = self.sqlite3_cursor.fetchall()
                self.results[token] = {"code": "0", "status": True, "rows": rows, "err": None}
            else:
                self.results[token] = {"code": "0", "status": True, "rows": None, "err": None}
            return True

        except sqlite3.Error as err:
            self.results[token] = {"code": "-1", "status": False, "rows": None, "err": err}
            self.LOGGER.error("Query returned error: %s: %s: %s", query, values, err)
            return False

    def close(self):
        """Close down the thread and close the sqlite3 database file."""
        self.exit_set = True
        self.sql_queue.put((self.exit_token, "", ""), timeout=5)
        # Sleep and check that the thread is done before returning.
        while self.thread_running:
            time.sleep(.01)  # Don't kill the CPU waiting.

    @property
    def queue_size(self):
        """Return the queue size."""
        return self.sql_queue.qsize()

    def query_results(self, token):
        """Get the query results for a specific token.

        Args: token: A uuid object of the query you want returned.

        Returns: Return the results of the query when it's executed by the thread.
        """
        delay = .001
        while True:
            if token in self.results:
                return_val = self.results[token]
                del self.results[token]
                return return_val
            # Double back on the delay to a max of 8 seconds.  This prevents
            # a long lived select statement from trashing the CPU with this
            # infinite loop as it's waiting for the query results.
            self.LOGGER.debug("Sleeping: %s %s", delay, token)
            time.sleep(delay)
            if delay < 8:
                delay += delay

    def execute(self, query, values=None):
        """Execute a query.
        单条sql执行语句，组成一个事务
        Args:
            query: The sql string using ? for placeholders of dynamic values.
            values: A tuple of values to be replaced into the ? of the query.

        Returns: If it's a select query it will return the results of the query.
        """
        if self.exit_set:
            self.LOGGER.debug("Exit set, not running: %s", query)
            return "Exit Called"

        self.LOGGER.debug("execute: %s", query)
        values = values or []
        # A token to track this query with.
        token = str(uuid.uuid4())
        # If it's a select we queue it up with a token to mark the results
        # into the output queue so we know what results are ours.
        self.sql_queue.put((token, query, values), timeout=5)
        return self.query_results(token)

    def begin_trans(self):
        # todo
        pass

    def end_trans(self):
        # todo
        pass

    @staticmethod
    def insert_sql(table: str, data: dict, ignore_keys: tuple = None):
        """
        sql_worker.execute("INSERT into tester values (?, ?)", ("2010-01-01 13:00:00", "bow"))
        :param data:
        :param table:
        :param ignore_keys:
        :return:
        """
        opr_key = data.keys()

        if ignore_keys is not None and len(ignore_keys) > 0:
            for __ in ignore_keys:
                for __inner__ in data.keys():
                    if str(__).lower() == str(__inner__).lower():
                        opr_key.remove(str(__))

        keys = ', '.join(opr_key)
        values = ", ".join(['?'] * len(opr_key))

        return "INSERT INTO {table} ({keys}) VALUES ({values})".format(table=table, keys=keys, values=values)
