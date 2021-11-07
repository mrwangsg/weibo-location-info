#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/28 10:31
# @Author  : sgwang
# @File    : main.py
# @Software: PyCharm
import re
import sys
import time
import traceback
from urllib import parse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as Exc
from selenium.webdriver.support.wait import WebDriverWait

import config
from db.init_sqlite3 import init_sqlite_db
from db.worker_sqlite3 import Sqlite3Worker
from handler.img_handler import Img_Handler
from model.weibo_location_info_model import Weibo_Location_Info
from model.weibo_location_url_info_model import Weibo_Location_Url_Info
from sta_info import WORK_SPACE, URL
from utils import browser
from utils.log_ger import log_ger
from utils.time_out import time_out


def do_task(driver, url, sql_worker, max_timestamp: int):
    """

    :param driver:
    :param url:
    :param sql_worker:
    :param max_timestamp:
    :return: 0:正常；-1:待刷新；-2:后面的数据已经不需要再遍历
    """
    try:
        # 打开地址
        driver.get(url)

        # 先校验cookie是否还有效
        active_flag = cookie_active(driver=driver)
        active_info = f'当前cookie值仍然有效！' if active_flag else f'当前cookie值已经失效，请重新登录！'
        log_ger.info(active_info)

        # 寻找微博文，展示的根目录，如果没找到，那就是没有加载到，可能断网啦
        tmp_xpath = '//*[@id="Pl_Core_MixedFeed__4"]'
        ele_feed_root = WebDriverWait(driver, time_out.s30).until(
            Exc.presence_of_element_located((By.XPATH, tmp_xpath)), message="页面，加载超时，请刷新重试！")

        # 继续寻找标签，如果超时，说明这一页已经没有微博文展示
        tmp_xpath = '//*[@id="Pl_Core_MixedFeed__4"]/div'
        WebDriverWait(ele_feed_root, time_out.s10).until(
            Exc.presence_of_element_located((By.XPATH, tmp_xpath)), message="页面微博文为空！")

        # 操作滚动条，加载更多的元素
        scroll_times = 0
        while True:
            try:
                scroll_bottom = "document.documentElement.scrollTop=30000"
                driver.execute_script(scroll_bottom)

                # 判断是否加载完全
                tmp_xpath = '//*[@class="W_pages"]'
                WebDriverWait(ele_feed_root, time_out.s10).until(
                    Exc.visibility_of_all_elements_located((By.XPATH, tmp_xpath)),
                    message="页面底部的分页栏，加载超时，请刷新重试！")
                break
            except Exception as ex:
                scroll_times += 1
                log_ger.info(f"加载超时，第{scroll_times}刷新加载！{ex}")
                if scroll_times >= 3:
                    raise Exception("页面底部的分页栏，加载超时，请检查网络状况！")

        # 如果微博文不为空，寻找class='WB_feed WB_feed_v3 WB_feed_v4'
        tmp_xpath = '//*[@class="WB_feed WB_feed_v3 WB_feed_v4"]/div[starts-with(@tbinfo,"ouid=")]'
        ele_feed_list = WebDriverWait(ele_feed_root, time_out.s10).until(
            Exc.visibility_of_all_elements_located((By.XPATH, tmp_xpath)), message="")

        tmp_css = 'div.WB_detail'
        for ele_item in ele_feed_list:
            # 微博文，唯一Id
            weibo_mid = ele_item.get_attribute('mid')

            # 接下来的信息，都从这里出发
            ele_web_detail = ele_item.find_element(By.CSS_SELECTOR, tmp_css)

            # 微博文，对应个人信息获取
            css_user_info = "div.WB_info > a"
            ele_user_info = ele_web_detail.find_element(By.CSS_SELECTOR, css_user_info)

            user_info_nick_name = ele_user_info.get_attribute('nick-name')
            user_info_home_page = ele_user_info.get_attribute('href')
            user_info_user_id = re.search(r'/(\w*)\?', user_info_home_page).group(1)

            # 微博文，链接，时间等信息获取
            css_from_info = 'div.WB_from > a[node-type="feed_list_item_date"]'
            ele_from_info = ele_web_detail.find_element(By.CSS_SELECTOR, css_from_info)

            from_info_url = ele_from_info.get_attribute('href')
            from_info_date = ele_from_info.get_attribute('title')
            from_info_timestamp = ele_from_info.get_attribute('date')

            # 插入比较时间戳。如果当前时间戳，比数据库以往数据都小，那么说明已经遍历过啦
            if int(from_info_timestamp) <= int(max_timestamp):
                return int(-2)

            # 微博文，来自，设备信息
            css_from_info = 'div.WB_from'
            ele_from_info = ele_web_detail.find_element(By.CSS_SELECTOR, css_from_info)

            from_info_device = re.search(r'来自 (.*)', ele_from_info.text)
            from_info_device = '' if from_info_device is None else from_info_device.group(1)

            # 微博文，文案
            css_content_info = 'div[node-type="feed_list_content"]'
            ele_content_info = ele_web_detail.find_element(By.CSS_SELECTOR, css_content_info)

            content_info_html_text = ele_content_info.get_attribute('innerHTML')
            content_info_simple_text = ele_content_info.text

            # todo 微博文，打卡地点。这个必须呀，因为主题就是收集打卡点
            content_info_location_list = []
            css_content_info = css_content_info + ' a[action-type="feed_list_url"] i.ficon_cd_place'
            ele_info_location_list = ele_web_detail.find_elements(By.CSS_SELECTOR, css_content_info)
            for _info_location in ele_info_location_list:
                content_info_location_list.append({
                    "text": _info_location.find_element(By.XPATH, './/..').text,
                    "url": _info_location.find_element(By.XPATH, './/..').get_attribute('href'),
                    "from_info_date": from_info_date,
                    "from_info_timestamp": from_info_timestamp,
                })

            # 微博文，图片、live图片、视频资源；   跳转链接
            css_media_box_info = 'div[node-type="feed_list_media_prev"] > div[class="media_box"]'
            data_media_video_id, data_media_video_tmp_url = '', ''
            data_media_img_list, data_media_jump_url = [], ''

            # 单段视频，type=001
            try:
                css_media_video_id = css_media_box_info + ' li[action-type="feed_list_third_rend"] video'
                ele_media_video_id = ele_web_detail.find_element(By.CSS_SELECTOR, css_media_video_id)
                data_media_video_id = ele_media_video_id.get_attribute('src')

                css_media_video_url = css_media_box_info + ' li[action-type="feed_list_third_rend"]'
                ele_media_video_url = ele_web_detail.find_element(By.CSS_SELECTOR, css_media_video_url)
                data_media_video_url = ele_media_video_url.get_attribute('action-data')

                # 需要两次url解码才行
                data_media_video_url = parse.unquote(parse.unquote(data_media_video_url))
                data_media_video_tmp_url = re.search(r'&video_src=(.*video)&', data_media_video_url).group(
                    1)

            except NoSuchElementException as ex_001:
                pass

            # 单张图片，type=002
            try:
                css_media_img = css_media_box_info + ' li[action-type="feed_list_media_img"] img'
                ele_media_img = ele_web_detail.find_element(By.CSS_SELECTOR, css_media_img)
                data_media_img_list.append(ele_media_img.get_attribute('src'))
            except NoSuchElementException as ex_002:
                pass

            # 集合图片，type=003
            try:
                css_media_img_list = css_media_box_info + ' li[action-type="fl_pics"] img'
                ele_media_img_list = ele_web_detail.find_elements(By.CSS_SELECTOR, css_media_img_list)
                for item_img in ele_media_img_list:
                    data_media_img_list.append(item_img.get_attribute('src'))
            except NoSuchElementException as ex_003:
                pass

            # 跳转链接，type=004
            try:
                css_jump_url = css_media_box_info + ' div[action-type="fl_jumpurl"] a'
                ele_jump_url = ele_web_detail.find_element(By.CSS_SELECTOR, css_jump_url)
                data_media_jump_url = ele_jump_url.get_attribute('href')
            except NoSuchElementException as ex_002:
                pass

            # 插入数据
            now_timestamp = int(time.time() * 1000)

            # 存储微博打卡
            weibo_location_info = Weibo_Location_Info()
            weibo_location_info.set_weibo_mid(weibo_mid)
            weibo_location_info.set_user_info_nick_name(user_info_nick_name)
            weibo_location_info.set_user_info_user_id(user_info_user_id)
            weibo_location_info.set_from_info_url(from_info_url)
            weibo_location_info.set_from_info_date(from_info_date)
            weibo_location_info.set_from_info_timestamp(from_info_timestamp)
            weibo_location_info.set_from_info_device(from_info_device)
            weibo_location_info.set_content_info_html_text(content_info_html_text)
            weibo_location_info.set_content_info_simple_text(content_info_simple_text)
            weibo_location_info.set_data_media_video_id(data_media_video_id)
            weibo_location_info.set_data_media_video_tmp_url(data_media_video_tmp_url)
            weibo_location_info.set_data_media_jump_url(data_media_jump_url)
            weibo_location_info.set_data_media_img_list(
                ';'.join(str(tmp_img) for tmp_img in data_media_img_list))

            weibo_location_info.set_status(int(0))
            weibo_location_info.set_is_delete(int(0))
            weibo_location_info.set_create_timestamp(now_timestamp)
            weibo_location_info.set_update_timestamp(now_timestamp)
            # 操作插入
            sql_str = sql_worker.insert_sql('weibo_location_info', weibo_location_info.__dict__)
            db_res = sql_worker.execute(sql_str, tuple(weibo_location_info.__dict__.values()))

            # 保存微博文对应的打卡地点信息
            for tmp_ in content_info_location_list:
                weibo_location_url_info = Weibo_Location_Url_Info()
                weibo_location_url_info.set_weibo_mid(weibo_mid)
                weibo_location_url_info.set_content_info_location_text(tmp_.get('text', ''))
                weibo_location_url_info.set_content_info_location_url(tmp_.get('url', ''))
                weibo_location_url_info.set_from_info_date(from_info_date)
                weibo_location_url_info.set_from_info_timestamp(from_info_timestamp)

                weibo_location_url_info.set_status(int(0))
                weibo_location_url_info.set_is_delete(int(0))
                weibo_location_url_info.set_create_timestamp(now_timestamp)
                weibo_location_url_info.set_update_timestamp(now_timestamp)
                # 操作插入
                sql_str = sql_worker.insert_sql('weibo_location_url_info', weibo_location_url_info.__dict__)
                db_res = sql_worker.execute(sql_str, tuple(weibo_location_url_info.__dict__.values()))

            log_ger.info(f'\n\t{weibo_mid};\t{user_info_nick_name};\t{user_info_user_id};'
                         f'\n\t{from_info_url};\t{from_info_date};\t{from_info_timestamp};\t{from_info_device};'
                         f'\n\tcontent_info_html_text:"";\t{content_info_simple_text};\t{content_info_location_list};'
                         f'\n\t{data_media_video_id};\t{data_media_video_tmp_url};'
                         f'\n\t{data_media_jump_url};\t{data_media_img_list}')
            log_ger.info('==' * 30)
            log_ger.info('==' * 30 + '\n\n')

        log_ger.info(f"当前分页：{url}，总共有{len(ele_feed_list)}个微博发文")
        time.sleep(time_out.s10)
        return int(0)

    except Exception as for_ex:
        log_ger.error(traceback.format_exc())
        return int(-1)


def cookie_active(driver: WebDriver):
    """
    判断cookie是否有效
    :param driver:
    :return:
    """
    if driver.current_url.startswith(URL.weibo_login_index_url):
        return False
    return True


def main(sql_worker: Sqlite3Worker):
    driver = None
    init_sub_cookie = {'name': 'SUB',
                       'value': '_2A25MgzTgDeRhGeNK7FAV9i3IzDSIHXVv-SEorDV8PUNbmtANLRmjkW9NSVqx_xX9AX1TjHs4-wEj1mYNoPD6gnte'}

    try:
        # 根据配置文件，初始化浏览器
        driver = browser.init_browser()
        driver.get(URL.weibo_index_url)
        time.sleep(time_out.s5)

        # 添加登录cookie
        login_cookies = driver.get_cookies()
        log_ger.info(f'添加前：cookie值{login_cookies}')
        driver.delete_all_cookies()
        driver.add_cookie({
            'name': init_sub_cookie['name'],
            'value': init_sub_cookie['value'],
        })
        login_cookies = driver.get_cookies()
        log_ger.info(f'添加后：cookie值{login_cookies}')

        while True:
            # 获取当前数据库，最大时间戳
            max_sql = 'SELECT IFNULL(MAX(from_info_timestamp), 0) FROM weibo_location_info limit 1;'
            max_res = sql_worker.execute(max_sql)
            max_timestamp = int(0)
            if max_res.get('status') and max_res.get('rows')[0] is not None and max_res.get('rows')[0][0] is not None:
                max_timestamp = int(max_res.get('rows')[0][0])

            for index in range(1, 28):
                url = f'https://weibo.com/p/1001018008645090000000000?current_page=3&since_id=&page={index}'
                flush_flag = do_task(driver, url, sql_worker, max_timestamp)

                if flush_flag == int(-1):
                    # 如果失败，只是刷新一遍
                    log_ger.info("刷新，再次尝试获取数据！")
                    do_task(driver, url, sql_worker, max_timestamp)

                elif flush_flag == int(-2):
                    # 这种情况，可以跳出循环
                    log_ger.info("后面的数据，已经遍历过，无需再遍历！！！")
                    break

            # 循环间隔时长
            time.sleep(config.cycle_wait_time)

    except Exception as main_ex:
        log_ger.error(traceback.format_exc())

    finally:
        # 关闭浏览器
        log_ger.info("程序运行结束！！！")

        if driver:
            driver.close()
            driver.quit()


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
    Img_Handler(_sql_worker).start_work()

    main(_sql_worker)
    sys.exit(0)
