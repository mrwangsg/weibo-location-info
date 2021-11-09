#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/28 10:31
# @Author  : sgwang
# @File    : main.py
# @Software: PyCharm
import queue
import sys
import time
import traceback

import config
from db.init_sqlite3 import init_sqlite_db
from db.worker_sqlite3 import Sqlite3Worker
from handler.img_handler import Img_Handler
from handler.pool_handler import Pool_Handler
from sta_info import WORK_SPACE, URL
from utils import browser
from utils.log_ger import log_ger
from utils.time_out import time_out


def check_cookie_active(cookie):
    driver = None

    try:
        # 根据配置文件，初始化浏览器
        driver = browser.init_browser()
        driver.get(URL.weibo_index_url)
        time.sleep(time_out.s10)

        # 添加登录cookie
        login_cookies = driver.get_cookies()
        log_ger.info(f'添加前：cookie值{login_cookies}')
        driver.delete_all_cookies()
        driver.add_cookie({'name': cookie['name'], 'value': cookie['value']})
        login_cookies = driver.get_cookies()
        log_ger.info(f'添加后：cookie值{login_cookies}')

        # 校验结果
        if driver.current_url.startswith(URL.weibo_login_index_url) \
                or driver.current_url.startswith(URL.weibo_user_index_url):
            log_ger.error('check_cookie_active(cookie)：当前cookie值已经失效，请重新登录！')
            return False

        log_ger.info('check_cookie_active(cookie)：当前cookie值仍然有效！')
        return True

    except Exception as ex:
        log_ger.error('check_cookie_active(cookie)：校验输入的cookie有效性时，出现异常！')
        log_ger.info(traceback.format_exc())

        if driver:
            driver.close()
            driver.quit()

        return False


def main(sql_worker: Sqlite3Worker, _pool_handler: Pool_Handler, city_code_list: list):
    try:
        while True:
            for city_code in city_code_list:
                for index in range(1, 28):
                    url = f'{URL.city_index_prefix}{city_code}{URL.city_index_suffix}' \
                          f'?current_page={(index - 1) * 3}&since_id=&page={index}#feedtop'
                    try:
                        _pool_handler.add_task(sql_worker, city_code, url)
                    except queue.Full as ex:
                        log_ger.error("队列已满，无法加入队列中！")
                        time.sleep(time_out.s3)

            # 循环间隔时长
            time.sleep(config.cycle_wait_time)

    except Exception as main_ex:
        log_ger.error(traceback.format_exc())
    finally:
        # 关闭浏览器
        log_ger.info("程序运行结束！！！")


if __name__ == "__main__":
    log_ger.info('hello weibo the location info!')
    log_ger.info(f'the program work root path: {WORK_SPACE.ROOT_PATH}')

    # 建立数据库连接
    db_file_name = config.db_sqlite3['ini_db_path']
    _sql_worker = Sqlite3Worker(db_file_name)

    # 创建数据库表
    sql_file_name = config.db_sqlite3['ini_sql_path']
    if init_sqlite_db(_sql_worker, sql_file_name):
        log_ger.info("数据表初始化成功！")
    else:
        log_ger.error("数据表初始化失败！")

    # 启动图片下载线程
    img_max_workers = config.img_handler.get('max_workers', int(2))
    img_thread_name_prefix = config.img_handler.get('thread_name_prefix', 'img_handler')
    img_root = config.img_handler.get('img_root', None)
    Img_Handler(_sql_worker, img_max_workers, img_thread_name_prefix, img_root=img_root).start_work()
    log_ger.info("图片下载器，初始化成功！")

    # 校验cookie的有效性，没有效可以直接退出程序！
    _cookie = config.wb_cookie
    if check_cookie_active(_cookie) is False:
        sys.exit(-1)

    # 初始化线程池
    pool_max_workers = config.pool_handler.get('max_workers', int(2))
    pool_thread_name_prefix = config.pool_handler.get('thread_name_prefix', 'pool_handler')
    _pool_handler = Pool_Handler(pool_max_workers, pool_thread_name_prefix, _cookie)
    log_ger.info("浏览器任务工作池，初始化成功！")

    # 启动任务
    _city_code_list = config.city_code_list
    main(_sql_worker, _pool_handler, _city_code_list)
    sys.exit(0)
