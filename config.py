#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/28 10:33
# @Author  : sgwang
# @File    : config.py
# @Software: PyCharm

"""
微博账号cookie
"""
wb_cookie = {
    'name': 'SUB',
    'value': '_2A25Mg7xMDeRhGeNK7FAV9i3IzDSIHXVv-KqErDV8PUNbmtANLWPWkW9NSVqx_3UZ-EbiA4ujmuf_daQUmp0xWxrR',
}

"""
设置sqlite数据库配置
"""
db_sqlite3 = {
    'ini_sql_path': 'C:\project\weibo-location-info\data\sql\weibo_location.sql',
    'ini_db_path': 'C:\project\weibo-location-info\data\db\weibo_location.db',
}

"""
工作线程池配置
"""
pool_handler = {
    'max_workers': int(2),
    'thread_name_prefix': 'weibo_location_info_',
}

"""
# selenium 相关
# selenium.browser_type: 浏览器类型
# selenium.head_less: 无头模式，是否弹出chrome浏览器。True，表示弹出；False表示，禁止弹出
# selenium.load_img: 是否加载图片。True，表示加载；False表示，禁止加载
# selenium.width: 浏览器初始-宽度
# selenium.height: 浏览器初始-高度
"""
selenium_config = {
    'browser_type': "chrome",
    'head_less': True,
    'load_img': False,
    'width': 650,
    'height': 900,
}

# user-agent 用户代理，可自行配置
user_agent = [
    'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
]

# 选项1：150；  选项2：360；    选项3：690；    选项4：2000；   选项5：large
download_img_size = int(5)

# 以秒为单位，每次循环间隔时间。建议一个小时
cycle_wait_time = int(30 * 60)
