#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/28 10:34
# @Author  : sgwang
# @File    : URL.py
# @Software: PyCharm

"""
微博首页，可用于获取游客cookie
"""
weibo_index_url = 'https://weibo.com/'

"""
城市首页地址，eg:
    北京市：https://www.weibo.com/p/1001018008611000000000000
    武汉市：https://www.weibo.com/p/1001018008642010000000000
    玉林市：https://www.weibo.com/p/1001018008645090000000000
"""
pc_city_index_prefix = 'https://www.weibo.com/p/10010180086'

"""
pc城市首页后缀
"""
common_city_index_suffix = '0000000000'

"""
登录首页
"""
weibo_login_index_url = 'https://weibo.com/login'
