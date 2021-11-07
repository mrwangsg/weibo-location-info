#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/30 16:25
# @Author  : sgwang
# @File    : init_sqlite3.py
# @Software: PyCharm

from db.worker_sqlite3 import Sqlite3Worker
from utils.log_ger import log_ger


def init_sqlite_db(sql_worker: Sqlite3Worker, sql_file_name):
    try:
        with open(sql_file_name, 'r', encoding='utf-8') as fr:
            exec_sql_list = fr.read().strip().split(';')

            # 创建数据表
            for exec_sql in exec_sql_list:
                if exec_sql.strip() != '':
                    sql_worker.execute(exec_sql.strip())
        return True
    except Exception as ex:
        log_ger.error(ex)
        return False


if __name__ == "__main__":
    # 建立数据库连接
    _db_file_name = 'C:\project\weibo-location-info\data\db\weibo_location.db'
    _sql_worker = Sqlite3Worker(_db_file_name)

    # 创建数据库表
    _sql_file_name = 'C:\project\weibo-location-info\data\sql\weibo_location.sql'
    init_sqlite_db(_sql_worker, _sql_file_name)
