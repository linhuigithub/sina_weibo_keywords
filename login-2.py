# -*- coding: utf-8 -*-

from time import sleep
import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class Login(object):

    def __init__(self):
        pass

    def main(self, user, passwd):
        # 设置头信息
        desired_capabilities = dict()
        desired_capabilities['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0'
        # 目的不确定
        service_args = list()
        service_args += ['---load-imges=false']
        DesiredCapabilities.PHANTOMJS.update(desired_capabilities)
        # 驱动Phanjs
        browser = webdriver.PhantomJS()
        # 设置分辨率（无界面浏览器，为何要设置分辨率？）
        browser.set_window_size(width=1366, height=768)
        # 设置等待页面加载时间
        browser.set_page_load_timeout(30)
        browser.get('http://weibo.com/login')
        # 帐号输入框
        try:
            browser.find_element_by_xpath('//*[@id="loginname"]').send_keys(user)
        except:
            print u'账号框定位失败'
        # 密码输入框
        try:
            browser.find_element_by_xpath('//*[@class="info_list password"]/div/input[@class="W_input"]').send_keys(
                passwd)
        except:
            print u'密码框定位失败'

        # 登录
        try:
            browser.find_element_by_xpath('//div[@class="info_list login_btn"]/a').click()
        except:
            print u'登录框定位失败'
        # 这两者有什么区别
        # sleep(10)
        WebDriverWait(browser, 30)
        cookies = browser.get_cookies()
        print browser.current_url
        cookie_s = dict()
        if browser.current_url.find('/home') != -1:
            for co in cookies:
                cookie_s[co.get('name')] = co.get('value')
            print json.dumps(cookie_s)

        browser.close()  # 关闭当前窗口
        browser.quit()  # 关闭所有窗口


if __name__ == '__main__':
    login = Login()
    login.main('账号', '密码')
