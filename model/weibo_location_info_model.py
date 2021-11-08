#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/30 23:32
# @Author  : sgwang
# @File    : weibo_location_info_model.py
# @Software: PyCharm
import time


class Weibo_Location_Info(object):

    def __init__(self):
        now_timestamp = int(time.time() * 1000)  # 毫秒级，13位

        self.id = None  # 使用自增Id
        self.weibo_mid = None  # 微博id
        self.city_code = None  # 城市编码
        self.user_info_nick_name = None  # 用户名
        self.user_info_user_id = None  # 用户id

        self.from_info_date = None  # 微博文，字符串时间
        self.from_info_timestamp = None  # 微博文，时间戳
        self.from_info_url = None  # 微博文，来源地址
        self.from_info_device = None  # 微博文，来源设备

        self.content_info_simple_text = None  # 微博正文，脱离html标签，内容
        self.content_info_html_text = None  # 微博正文，包含html标签，内容

        self.data_media_video_id = None  # 视频id
        self.data_media_video_tmp_url = None  # 有时效性的视频地址
        self.data_media_img_list = None  # 图片集合
        self.data_media_jump_url = None  # 跳转链接地址

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

    def set_city_code(self, city_code):
        self.city_code = city_code

    def get_city_code(self):
        return self.city_code

    def set_user_info_nick_name(self, user_info_nick_name):
        self.user_info_nick_name = user_info_nick_name

    def get_user_info_nick_name(self):
        return self.user_info_nick_name

    def set_user_info_user_id(self, user_info_user_id):
        self.user_info_user_id = user_info_user_id

    def get_user_info_user_id(self):
        return self.user_info_user_id

    def set_from_info_date(self, from_info_date):
        self.from_info_date = from_info_date

    def get_from_info_date(self):
        return self.from_info_date

    def set_from_info_timestamp(self, from_info_timestamp):
        self.from_info_timestamp = from_info_timestamp

    def get_from_info_timestamp(self):
        return self.from_info_timestamp

    def set_from_info_url(self, from_info_url):
        self.from_info_url = from_info_url

    def get_from_info_url(self):
        return self.from_info_url

    def set_from_info_device(self, from_info_device):
        self.from_info_device = from_info_device

    def get_from_info_device(self):
        return self.from_info_device

    def set_content_info_simple_text(self, content_info_simple_text):
        self.content_info_simple_text = content_info_simple_text

    def get_content_info_simple_text(self):
        return self.content_info_simple_text

    def set_content_info_html_text(self, content_info_html_text):
        self.content_info_html_text = content_info_html_text

    def get_content_info_html_text(self):
        return self.content_info_html_text

    def set_data_media_video_id(self, data_media_video_id):
        self.data_media_video_id = data_media_video_id

    def get_data_media_video_id(self):
        return self.data_media_video_id

    def set_data_media_video_tmp_url(self, data_media_video_tmp_url):
        self.data_media_video_tmp_url = data_media_video_tmp_url

    def get_data_media_video_tmp_url(self):
        return self.data_media_video_tmp_url

    def set_data_media_img_list(self, data_media_img_list):
        self.data_media_img_list = data_media_img_list

    def get_data_media_img_list(self):
        return self.data_media_img_list

    def set_data_media_jump_url(self, data_media_jump_url):
        self.data_media_jump_url = data_media_jump_url

    def get_data_media_jump_url(self):
        return self.data_media_jump_url

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
    weibo_location_info = Weibo_Location_Info()

    for _ in weibo_location_info.__dict__:
        print('def set_' + _ + '(self, ' + _ + '):')
        print('\tself.' + _ + ' = ' + _)

        print('def get_' + _ + '(self):')
        print('\treturn self.' + _)
