#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/28 10:31
# @Author  : sgwang
# @File    : log_ger.py
# @Software: PyCharm
import logging
import os
import time
from logging import handlers

from sta_info import WORK_SPACE

# 工作根目录
root_work = WORK_SPACE.ROOT_PATH
# 日志目录
logs_dir = os.path.join(root_work, 'logs')


class inner_log(object):
    """
    输出日志类
    """

    def __init__(self):
        self.logger = logging.getLogger("")

        if not os.path.exists(logs_dir):
            os.mkdir(logs_dir)

        # 设置日志文件名和日志格式
        log_file = time.strftime("%Y%m%d", time.localtime()) + ".log"
        log_path = os.path.join(logs_dir, log_file)

        # 追加写入日志
        format_str = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        file_handler = handlers.RotatingFileHandler(filename=log_path, encoding="utf-8")
        file_handler.setFormatter(format_str)

        # 终端输出
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(format_str)

        # 绑定 handler
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)

    def instance(self):
        return self.logger


log_ger = inner_log().instance()

if __name__ == "__main__":
    log_ger.info("Test info")
    log_ger.error("Test error")
