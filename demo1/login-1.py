# -*- coding:utf-8 -*-

__author__ = 'lh'

import time
import base64
import rsa
import binascii
import requests
import re
from requests.adapters import HTTPAdapter
from urllib import quote_plus
import json


class weibo_login():
    def __init__(self):
        # 构造 Request headers
        agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
        self.headers = {'User-Agent': agent}

        # 访问 初始页面带上 cookie

        self.session = requests.session()
        self.session.mount('http://', HTTPAdapter(max_retries=5))
        # index_url = "http://weibo.com/login.php"

    def get_su(self, username):

        """
        对 email 地址和手机号码 先 javascript 中 encodeURIComponent
        对应 Python 中的是 urllib.quote_plus
        然后在 base64 加密后decode
        """
        username_quote = quote_plus(username)
        username_base64 = base64.b64encode(username_quote.encode("utf-8"))
        return username_base64.decode("utf-8")

    # 预登陆获得 servertime, nonce, pubkey, rsakv
    def get_server_data(self, su):
        pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="
        pre_url = pre_url + su + "&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_="
        prelogin_url = pre_url + str(int(time.time() * 1000))
        pre_data_res = self.session.get(prelogin_url, headers=self.headers, timeout=10)
        sever_data = eval(pre_data_res.content.decode("utf-8").replace("sinaSSOController.preloginCallBack", ''))
        return sever_data

    # 这一段用户加密密码，需要参考加密文件
    def get_password(self,password, servertime, nonce, pubkey):
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥,
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)  # 拼接明文js加密文件中得到
        message = message.encode("utf-8")
        passwd = rsa.encrypt(message, key)  # 加密
        passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
        return passwd

    def coo_dict(self, cookies):
        dict_cookies = requests.utils.dict_from_cookiejar(cookies)
        print dict_cookies
        with open('cookies_file.txt', 'w') as f:
            f.write(json.dumps(
                dict_cookies))
            f.close()

    def login(self, username, password):
        # su 是加密后的用户名
        su = self.get_su(username)
        sever_data = self.get_server_data(su)
        servertime = sever_data["servertime"]
        nonce = sever_data['nonce']
        rsakv = sever_data["rsakv"]
        pubkey = sever_data["pubkey"]
        password_secret = self.get_password(password, servertime, nonce, pubkey)

        postdata = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'useticket': '1',
            'pagerefer': "http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl",
            'vsnf': '1',
            'su': su,
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'rsakv': rsakv,
            'sp': password_secret,
            'sr': '1366*768',
            'encoding': 'UTF-8',
            'prelt': '115',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
            }
        login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        login_page = self.session.post(login_url, data=postdata, headers=self.headers, timeout=10)
        s = self.session.cookies
        self.coo_dict(s)

        login_loop = (login_page.content.decode("GBK"))
        pa = r'location\.replace\([\'"](.*?)[\'"]\)'
        loop_url = re.findall(pa, login_loop)[0]
        login_index = self.session.get(loop_url, headers=self.headers, timeout=6)
        uuid = login_index.text
        uuid_pa = r'"uniqueid":"(.*?)"'
        uuid_res = re.findall(uuid_pa, uuid, re.S)[0]
        web_weibo_url = "http://weibo.com/%s/profile?topnav=1&wvr=6&is_all=1" % uuid_res
        try:
            weibo_page = self.session.get(web_weibo_url, headers=self.headers, timeout=6)

            weibo_pa = r'<title>(.*?)</title>'
            userName = re.findall(weibo_pa, weibo_page.content.decode("utf-8", 'ignore'), re.S)[0]
            print u'登陆成功，你的用户名为：'+userName
        except:
            print u'用户名获取失败'


if __name__ == "__main__":
    login = weibo_login()
    login.login('ckqsars@sina.com', 'ckqsars0306')
