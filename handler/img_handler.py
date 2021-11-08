#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/2 21:57
# @Author  : sgwang
# @File    : img_handler.py
# @Software: PyCharm
import os
import random
import sys
import threading
import time

import requests as requests
import urllib3
from requests.adapters import HTTPAdapter

import config
from db.init_sqlite3 import init_sqlite_db
from db.worker_sqlite3 import Sqlite3Worker
from sta_info import WORK_SPACE
from utils.log_ger import log_ger
# 工作根目录
from utils.time_out import time_out

root_work = WORK_SPACE.ROOT_PATH
# 图片目录
img_dir = os.path.join(root_work, 'data', 'img')

# 关闭警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 随机获取一个user_agent
user_agent = config.user_agent[random.randint(0, len(config.user_agent) - 1)]

# 设置会话连接限制
session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3, pool_maxsize=3))
session.mount('https://', HTTPAdapter(max_retries=3, pool_maxsize=3))

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

    def __init__(self, sql_worker: Sqlite3Worker):
        threading.Thread.__init__(self)
        self.daemon = True

        self.sql_worker = sql_worker

        if not os.path.exists(img_dir):
            os.mkdir(img_dir)
        pass

    def run(self):
        while True:
            try:
                ret_flag = download_2_local(self.sql_worker)
                if ret_flag == int(0):
                    time.sleep(time_out.m1)

                if ret_flag == int(-1):
                    time.sleep(time_out.s10)
            except Exception as ex:
                log_ger.error(ex)

    def start_work(self):
        self.start()
        pass


def download_2_local(sql_worker: Sqlite3Worker):
    # 查询数据库，获取图片list地址
    select_sql = f"""Select id, data_media_img_list, from_info_timestamp, user_info_nick_name from weibo_location_info where status=0 and is_delete=0 order by id asc limit 1;"""
    result = sql_worker.execute(select_sql)
    if result['status'] is False:
        log_ger.error(result['err'])
        return int(-1)
    if len(result['rows']) == int(0):
        return int(0)

    # 下载图片
    row = result['rows'][0]
    data_media_img_list = row[1]
    if len(data_media_img_list.strip()) > 0:
        img_url_list = data_media_img_list.split(';')
        for img_url in img_url_list:
            if down_img(img_url, row[2], row[3]) is False:
                return int(-1)

    update_sql = f"""update weibo_location_info set status=1  where id={row[0]} """
    result = sql_worker.execute(update_sql)
    if result['status'] is False:
        log_ger.error(result['err'])
        return int(-1)

    return int(1)


def down_img(img_url, timestamp, user_name):
    for _ in all_img_size.values():
        img_url = img_url.replace(_, default_img_size)

    file_name = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(int(timestamp) / 1000)) + ' ' + user_name + ' ' + \
                img_url.split('/')[-1]

    headers = {'User_Agent': user_agent}
    result = session.get(img_url, headers=headers, timeout=time_out.s10, verify=False)

    if result.status_code == 200:
        with open(os.path.join(img_dir, file_name), 'wb') as fr:
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

    img_handler = Img_Handler(_sql_worker)
    sys.exit(0)
