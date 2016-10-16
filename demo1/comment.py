# -*- coding: utf-8 -*-

from SpiderInterface.queue.QueueFactory import QueueFactory
from SpiderInterface.field.FieldFactory import FieldFactory
from requests.adapters import HTTPAdapter
from common import config
from lxml import etree
import private_config
import requests
import json
import time


class Comment(object):

    def __init__(self):
        self.queue_redis = QueueFactory()
        self.field_factory = FieldFactory(u'微博关键字-评论')
        self.db_factory = QueueFactory()
        self.db = self.db_factory.create(config.db_type, private_config.comment_weibo,
                                         config.db_host, config.db_port)
        self.queue_cookies = self.queue_redis.create(config.queue_type, private_config.cookie,
                                                     config.queue_host, config.queue_port)
        self.queue_mid = self.queue_redis.create(config.queue_type, private_config.mid,
                                                 config.queue_host, config.queue_port)

    def getcookies(self):
        cookies = self.queue_cookies.get()
        if not cookies:
            print u'cookies等待中...'
            time.sleep(60)
            return self.getcookies()
        else:
            self.queue_cookies.put(cookies)
            return cookies

    def GetHeader(self, url):
        header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                  'Accept-Encoding': 'gzip, deflate',
                  'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                  'Connection': 'keep-alive',
                  'Content-Type': 'application/x-www-form-urlencoded',
                  'Host': 'weibo.com',
                  'Referer': url,
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0',
                  'X-Requested-W'
                  'ith': 'XMLHttpRequest',
                  }
        return header

    def GetPage(self, mid, page):
        url = 'http://weibo.com/aj/v6/comment/big?ajwvr=6&id=%s&page=%s' % (mid, page)
        print url
        browser = requests.session()
        browser.cookies = self.getcookies()
        browser.mount('http://', HTTPAdapter(max_retries=5))
        header = self.GetHeader(url)
        try:
            html = browser.get(url, headers=header, timeout=10).content
        except Exception as e:
            print e
            return
        content = json.loads(html)['data']['html']
        return content

    def main(self):
        mid_num = self.queue_mid.get().split('@@@@')
        print mid_num
        mid = mid_num[0]
        pageall = int(mid_num[1])/20+1
        print pageall
        for page in xrange(1, pageall+1):
            html = self.GetPage(mid, str(page))
            if html:
                tree_all = etree.HTML(html)
                content = tree_all.xpath('//div[@class="list_li S_line1 clearfix"]')
                newslist = [etree.tostring(value) for value in content]
                field = self.field_factory.create('comment_ziduan')
                for item in newslist:
                    tree = etree.HTML(item)
                    # 用户正文url
                    weibo_url = mid
                    field.set('weibo_url', weibo_url)
                    # 用户名
                    yong_hu_ming = tree.xpath('//div[@class="WB_text"]/a[1]/text()')[0]
                    field.set('yong_hu_ming', yong_hu_ming)
                    # 评论内容
                    ping_lun_nei_rong = ''.join(tree.xpath('//div[@class="WB_text"]/text()'))
                    field.set('ping_lun_nei_rong', ping_lun_nei_rong)
                    # 用户ID
                    yong_hu_ID = tree.xpath('//div[@class="WB_text"]/a[1]/@usercard')[0]
                    field.set('yong_hu_ID', yong_hu_ID)
                    # 微博认证
                    try:
                        wei_bo_ren_zheng = tree.xpath('//div[@class="WB_text"]/a[2]/i/@title')[0]
                    except:
                        wei_bo_ren_zheng = ''
                    field.set('wei_bo_ren_zheng', wei_bo_ren_zheng)
                    # 评论时间
                    ping_lun_shi_jian = tree.xpath('//div[@class="WB_func clearfix"]/div[2]/text()')[0]
                    field.set('ping_lun_shi_jian', ping_lun_shi_jian)
                    # 点赞数
                    field.set('id', yong_hu_ID+'@@@@'+ping_lun_shi_jian)
                    data = field.make()
                    if data:
                        # self.db.put(data)
                        print json.dumps(data, ensure_ascii=False, indent=4)
                        # print '评论获取成功'


if __name__ == '__main__':
    com = Comment()
    com.main()

