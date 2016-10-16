# -*- coding:utf-8 -*-
import requests


def browser(url, retries=5, headers=None, timeout=10):
    global flag
    flag = retries

    def retry():
        global flag
        try:
            print '倒数第%d尝试' % flag
            response = requests.get(url, headers, timeout=timeout)
            code = response.status_code
        except Exception as e:
            print e
            code = 0
        if code != 200:
            flag -= 1
            if flag <= 0:
                print '获取页面失败'
                return
            return retry()
        else:
            return response.content
    return retry()