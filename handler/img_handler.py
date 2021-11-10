#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/2 21:57
# @Author  : sgwang
# @File    : img_handler.py
# @Software: PyCharm
import os
import queue
import random
import sys
import threading
import time
import traceback

import requests as requests
import urllib3
from requests import Session
from requests.adapters import HTTPAdapter

import config
from db.init_sqlite3 import init_sqlite_db
from db.worker_sqlite3 import Sqlite3Worker
from sta_info import WORK_SPACE
from utils.log_ger import log_ger
# 工作根目录
from utils.time_out import time_out

# 项目根目录
root_work = WORK_SPACE.ROOT_PATH

# 关闭警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 随机获取一个user_agent
user_agent = config.user_agent[random.randint(0, len(config.user_agent) - 1)]

# 图片下载尺寸, 默认下载尺寸
all_img_size = {
    '1': 'thumb150',
    '2': 'orj360',
    '3': 'mw690',
    '4': 'mw2000',
    '5': 'large',
}
default_img_size = all_img_size.get(str(config.download_img_size), '3')


class Img_Handler(threading.Thread):

    def __init__(self, sql_worker: Sqlite3Worker, max_workers, thread_name_prefix, img_root=None):
        threading.Thread.__init__(self)
        self.daemon = True
        self.sql_worker = sql_worker
        self.max_workers = max_workers

        # 设置会话连接限制
        session = requests.Session()
        session.mount('http://', HTTPAdapter(max_retries=2, pool_maxsize=max_workers * 2))
        session.mount('https://', HTTPAdapter(max_retries=2, pool_maxsize=max_workers * 2))
        self.session = session

        # 创建图片存储根目录
        if img_root is None:
            # 默认图片目录
            img_root = os.path.join(root_work, 'data', 'img')
            if not os.path.exists(img_root):
                os.mkdir(img_root)
        self.default_img_dir = img_root
        log_ger.info(f"图片存储目录为：{self.default_img_dir}")

        # 创建数据缓存队列
        self.task_queue = queue.Queue(maxsize=100 * max_workers)
        self.task_work_pool = [Inner_Work(thread_name_prefix + str(_), self.task_queue, self.sql_worker,
                                          self.session, self.default_img_dir) for _ in range(0, max_workers)]

    def run(self):
        while True:
            try:
                if self.task_queue.qsize() <= self.max_workers:
                    # 查询数据库，获取图片list地址
                    select_sql = f"""Select id, data_media_img_list, from_info_timestamp, user_info_nick_name, city_code 
                                        from weibo_location_info where status=0 and is_delete=0 
                                        order by from_info_timestamp DESC limit {10 * self.max_workers};"""
                    result = self.sql_worker.execute(select_sql)

                    if result['status'] is False:
                        log_ger.error(result['err'])
                        continue

                    if len(result['rows']) == int(0):
                        continue

                    # 数据一行行塞入队列
                    for row in result['rows']:
                        self.task_queue.put(row)

            except Exception as ex:
                log_ger.error(ex)

            finally:
                # 间隔一秒查询一次
                time.sleep(time_out.s1)

    def start_work(self):
        self.start()
        pass


class Inner_Work(threading.Thread):

    def __init__(self, thread_name, task_queue, sql_worker: Sqlite3Worker, session: Session, default_img_dir: str):
        threading.Thread.__init__(self)
        self.daemon = True
        self.name = thread_name
        self.task_queue = task_queue
        self.sql_worker = sql_worker
        self.session = session
        self.default_img_dir = default_img_dir

        # 启动容器
        self.start()

    def run(self):
        # id, data_media_img_list, from_info_timestamp, user_info_nick_name, city_code
        # 用法：如果队列返回一个None值时，抛出StopIteration异常，即循环结束
        for row in iter(self.task_queue.get, None):
            try:
                # 下载图片
                data_media_img_list = row[1]
                if len(data_media_img_list.strip()) > 0:
                    img_url_list = data_media_img_list.split(';')
                    for img_url in img_url_list:
                        if down_img(self.session, self.default_img_dir, img_url, row[2], row[3], row[4]) is False:
                            # 下载失败时，暂停一会
                            time.sleep(time_out.s10)

                # 下载成功，更新状态
                update_sql = f"""update weibo_location_info set status=1  where id={row[0]} """
                result = self.sql_worker.execute(update_sql)
                log_ger.info(f'图片下载成功，相关信息：{row}')
                if result['status'] is False:
                    log_ger.error(result['err'])
                    time.sleep(time_out.s10)

            except Exception as ex:
                log_ger.error(f'图片下载任务异常！详细信息：{traceback.format_exc()}')


def down_img(session: Session, default_img_dir, img_url, timestamp, user_name, city_code):
    for _ in all_img_size.values():
        img_url = img_url.replace(_, default_img_size)

    file_name = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(int(timestamp) / 1000)) + ' ' + user_name + ' ' + \
                img_url.split('/')[-1]

    # 如果路径不存在，则创建
    file_path = os.path.join(default_img_dir, city_code)
    if not os.path.exists(file_path):
        os.mkdir(file_path)

    headers = {'User_Agent': user_agent}
    result = session.get(img_url, headers=headers, timeout=time_out.s10, verify=False)
    if result.status_code == 200:
        with open(os.path.join(file_path, file_name), 'wb') as fr:
            fr.write(result.content)
            return True
    return False


if __name__ == "__main__":
    # 建立数据库连接
    db_file_name = config.db_sqlite3['ini_db_path']
    _sql_worker = Sqlite3Worker(db_file_name)

    # 创建数据库表
    sql_file_name = config.db_sqlite3['ini_sql_path']
    if init_sqlite_db(_sql_worker, sql_file_name):
        log_ger.info("数据表初始化成功！")
    else:
        log_ger.error("数据表初始化失败！")

    img_handler = Img_Handler(_sql_worker, max_workers=2, thread_name_prefix='down_img_')
    sys.exit(0)
