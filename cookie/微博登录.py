import json
import re
import time
from io import BytesIO

import requests
from PIL import Image

qr_image_url_prefix = 'https://login.sina.com.cn/sso/qrcode/image?entry=weibo&size=180&callback=STK_'
qr_check_url_prefix = 'https://login.sina.com.cn/sso/qrcode/check?entry=sso&qrid='
login_set_cookie_url_prefix = 'https://login.sina.com.cn/sso/login.php?entry=qrcodesso&returntype=TEXT&crossdomain=1&cdult=3&domain=weibo.com&alt='

success_ret_code = '20000000'

if __name__ == "__main__":
    #  --二维码获取
    qr_all_url = qr_image_url_prefix + str(int(time.time()))
    qr_json = json.loads(re.findall(r'[(](.*?)[)]', requests.get(qr_all_url).text)[0])["data"]
    # 二维码地址 和 二维码校验Id
    qr_url, qr_id = qr_json['image'], qr_json['qrid']

    # 使用系统默认工具 暂时二维码
    qr_img_echo = BytesIO(requests.get('https:' + qr_url).content)
    Image.open(qr_img_echo).show()

    #  --扫码验证
    qr_check_url = qr_check_url_prefix + qr_id + '&callback=STK_' + str(int(time.time()))
    qr_check_resp, wait_time = requests.get(qr_check_url), 3 * 60
    while wait_time >= 0 and success_ret_code not in qr_check_resp.text:
        qr_check_resp = requests.get(qr_check_url)
        wait_time -= 3
        time.sleep(3)

    alt_url = json.loads(re.findall(r'[(](.*?)[)]', qr_check_resp.text)[0])['data']['alt']
    core_url = login_set_cookie_url_prefix + alt_url + '&savestate=30&callback=STK_' + str(int(time.time()))
    login_resp = requests.get(core_url).headers

    # 提取权限cookie
    weibo_cookies = dict(login_resp)['Set-Cookie']
    weibo_login_auth_cookie = 'SUB=' + re.findall('SUB=(.*?);', weibo_cookies)[0]
    print(weibo_login_auth_cookie)
