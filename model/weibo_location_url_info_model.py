#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/30 23:52
# @Author  : sgwang
# @File    : weibo_location_url_info_model.py
# @Software: PyCharm
import time


class Weibo_Location_Url_Info(object):

    def __init__(self):
        now_timestamp = int(time.time() * 1000)  # 毫秒级，13位

        self.id = None  # 使用自增Id
        self.weibo_mid = None  # 微博id

        self.content_info_location_text = None  # 微博正文，打卡地址(文字)
        self.content_info_location_url = None  # 微博正文，打卡地址(链接)
        self.from_info_date = None  # 微博文，字符串时间
        self.from_info_timestamp = None  # 微博文，时间戳

        self.status = int(0)  # 数据状态，用于后期分析数据
        self.is_delete = int(0)  # 删除状态，0表示未删除，1表示删除
        self.create_timestamp = now_timestamp
        self.update_timestamp = now_timestamp

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_weibo_mid(self, weibo_mid):
        self.weibo_mid = weibo_mid

    def get_weibo_mid(self):
        return self.weibo_mid

    def set_content_info_location_text(self, content_info_location_text):
        self.content_info_location_text = content_info_location_text

    def get_content_info_location_text(self):
        return self.content_info_location_text

    def set_content_info_location_url(self, content_info_location_url):
        self.content_info_location_url = content_info_location_url

    def get_content_info_location_url(self):
        return self.content_info_location_url

    def set_from_info_date(self, from_info_date):
        self.from_info_date = from_info_date

    def get_from_info_date(self):
        return self.from_info_date

    def set_from_info_timestamp(self, from_info_timestamp):
        self.from_info_timestamp = from_info_timestamp

    def get_from_info_timestamp(self):
        return self.from_info_timestamp

    def set_status(self, status):
        self.status = status

    def get_status(self):
        return self.status

    def set_is_delete(self, is_delete):
        self.is_delete = is_delete

    def get_is_delete(self):
        return self.is_delete

    def set_create_timestamp(self, create_timestamp):
        self.create_timestamp = create_timestamp

    def get_create_timestamp(self):
        return self.create_timestamp

    def set_update_timestamp(self, update_timestamp):
        self.update_timestamp = update_timestamp

    def get_update_timestamp(self):
        return self.update_timestamp


if __name__ == "__main__":
    weibo_location_url_info = Weibo_Location_Url_Info()

    for _ in weibo_location_url_info.__dict__:
        print('def set_' + _ + '(self, ' + _ + '):')
        print('\tself.' + _ + ' = ' + _)

        print('def get_' + _ + '(self):')
        print('\treturn self.' + _)
