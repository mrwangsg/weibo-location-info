import os
import random
import traceback

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

import config
from sta_info import WORK_SPACE
from utils.log_ger import log_ger


def init_browser():
    """
    获取浏览器对象
    :return:
    """
    default_binary_path = os.path.join(WORK_SPACE.ROOT_PATH, 'drivers', 'chromedriver')

    # 加载自定义配置
    selenium_config = config.selenium_config
    browser_type = selenium_config['browser_type']
    head_less = selenium_config['head_less']
    load_img = selenium_config['load_img']
    width = selenium_config['width']
    height = selenium_config['height']

    # 随机获取一个user_agent
    user_agent = config.user_agent[random.randint(0, len(config.user_agent) - 1)]

    try:
        if browser_type.lower() == 'chrome':
            options = webdriver.ChromeOptions()

            # 配置代理
            # options.add_argument('--proxy-server=http://ip:port')

            # 取消沙盒模式，解决DevToolsActivePort文件不存在的报错
            options.add_argument('--no-sandbox')
            # 禁用通知警告
            options.add_argument('–disable-notifications')
            # 针对Linux环境下的chrome参数。大量渲染时，写入/tmp而非/dev/shm
            options.add_argument('--disable-dev-shm-usage')
            # 反爬虫识别，window.navigator.webdriver='undefined'。版本94 正式版
            options.add_argument('--disable-blink-features=AutomationControlled')
            # 设置user-agent
            options.add_argument(f'--user-agent={user_agent}')

            if head_less:
                # 无界面模式
                options.add_argument('--headless')
                # 禁用gpu渲染
                options.add_argument('--disable-gpu')
                # 禁用GPU程序缓存
                options.add_argument('--disable-gpu-program-cache')
                # 禁用3D软件光栅化器的使用
                options.add_argument('--disable-software-rasterizer')

            # 1是加载图片，2是不加载图片
            load_img_flag = int(1) if load_img else int(2)
            options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": load_img_flag})
            # 不显示chrome正受到自动测试软件的控制。地址栏位置
            options.add_experimental_option("excludeSwitches", ['enable-automation'])

            # 加载驱动
            _browser = webdriver.Chrome(executable_path=default_binary_path, options=options)
            _browser.set_window_size(width, height)
        else:
            raise WebDriverException
        return _browser
    except WebDriverException as ex:
        # 驱动问题
        log_ger.error(traceback.format_exc())
