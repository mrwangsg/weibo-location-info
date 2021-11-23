#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/10 20:56
# @Author  : sgwang
# @File    : recover_data.py
# @Software: PyCharm
import re
import sqlite3
import sys
import time

import config
from db.init_sqlite3 import init_sqlite_db
from db.worker_sqlite3 import Sqlite3Worker
from model.weibo_location_url_info_model import Weibo_Location_Url_Info


def main():
    # 建立数据库连接
    db_file_name = config.db_sqlite3['ini_db_path']
    _sql_worker = Sqlite3Worker(db_file_name)

    # 创建数据库表
    sql_file_name = config.db_sqlite3['ini_sql_path']
    if init_sqlite_db(_sql_worker, sql_file_name):
        print("数据表初始化成功！")
    else:
        print("数据表初始化失败！")

    page_index, page_count, now_timestamp, = -1, 1000, int(time.time() * 1000)
    while True and page_index * page_count < 33139:
        page_index += 1
        select_sql = f"""Select content_info_html_text, weibo_mid, from_info_date, from_info_timestamp, city_code 
            from weibo_location_info  order by id DESC limit {page_index * page_count}, {page_count};"""
        result = _sql_worker.execute(select_sql)
        if result['status'] is False:
            print(result['err'])
            continue
        if len(result['rows']) == int(0):
            break

        # 将地址信息记录下来，批量执行
        weibo_location_url_info_list = []

        # 遍历每一行
        for record in result['rows']:
            # 数据库取出数据
            info_html = record[0]
            if info_html is None:
                continue

            # 匹配出地址信息
            place_res = re.findall(r'<i class="W_ficon ficon_cd_place">2</i>(.+?)</a>', info_html)

            # 地址信息去重处理
            place_res = list(set(place_res))

            # 不为空时，保存到数据库
            print(f'该条微博：{record[1]}，一共有{len(place_res)}地址信息。详情：{place_res}')
            if len(place_res) == 0:
                continue

            # 提取地址对应url信息
            for place_name in place_res:
                se_place_name = str(place_name).replace('(', '\\(').replace(')', '\\)').replace('[', '\\[').replace(']',
                                                                                                                    '\\]')
                se_str = f'title="{se_place_name}" href="(.+?)" alt='
                se_res = re.search(se_str, info_html)

                # 构建数据: Select content_info_html_text, weibo_mid, from_info_date, from_info_timestamp
                weibo_location_url_info = Weibo_Location_Url_Info()
                weibo_location_url_info.set_content_info_location_text('2' + place_name)
                weibo_location_url_info.set_content_info_location_url(se_res.group(1))
                weibo_location_url_info.set_weibo_mid(record[1])
                weibo_location_url_info.set_from_info_date(record[2])
                weibo_location_url_info.set_from_info_timestamp(record[3])
                weibo_location_url_info.set_city_code(record[4])

                weibo_location_url_info.set_status(int(0))
                weibo_location_url_info.set_is_delete(int(0))
                weibo_location_url_info.set_create_timestamp(now_timestamp)
                weibo_location_url_info.set_update_timestamp(now_timestamp)

                # 先缓存数据
                weibo_location_url_info_list.append(tuple(weibo_location_url_info.__dict__.values()))

                # # 操作插入
                # sql_str = _sql_worker.insert_sql('weibo_location_url_info', weibo_location_url_info.__dict__)
                # db_res = _sql_worker.execute(sql_str, tuple(weibo_location_url_info.__dict__.values()))
                # if db_res['status'] is False:
                #     print(f'插入数据异常：{db_res["err"]}')
                #     time.sleep(1)
                #     db_res = _sql_worker.execute(sql_str, tuple(weibo_location_url_info.__dict__.values()))
                #     if db_res['status'] is False:
                #         print(f'再执行一次插入数据，依旧异常：{db_res["err"]}。跳出此次插入。相关信息：{record}')
                #         continue

        # 操作插入
        try:
            sql_str = _sql_worker.insert_sql('weibo_location_url_info', Weibo_Location_Url_Info().__dict__)
            _sql_worker.sqlite3_cursor.executemany(sql_str, tuple(weibo_location_url_info_list))
        except sqlite3.Error as err:
            print(f'插入数据异常：{err}。相关信息：{result["rows"]}')
            return False


if __name__ == '__main__':
    main()
    sys.exit(0)
