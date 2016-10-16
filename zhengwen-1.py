# -*- coding: utf-8 -*-

"""
weibo的正文没有cookies只能获取到一页的数据
"""

from SpiderInterface.field.FieldFactory import FieldFactory
from common import xpathutil
from lxml import etree
import requests
import json
import re


class zhengwen(object):

    def __init__(self):
        self.session = requests.Session()
        self.field_factory = FieldFactory(u'微博正文')

    def getheader(self, url):
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 's.weibo.com',
            'Referer': url,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
                  }
        return header

    def dict_coo(self):
        with open('cookies_file.txt', 'r') as f:
            file = f.read()
            file = json.loads(file)
            f.close()
        cookies = requests.utils.cookiejar_from_dict(file, cookiejar=None, overwrite=True)
        return cookies

    def gethtml(self):
        try:
            url = 'http://s.weibo.com/weibo/%25E8%25A5%25BF%25E5%258D%2597%25E7%259F%25B3%25E6%25B2%25B9%25E5%25A4%25A7%25E5%25AD%25A6&page=1'
            self.session.cookies = self.dict_coo()
            html = self.session.get(url, headers=self.getheader(url), timeout=15).content
            return html
        except Exception as e:
            print e
            return

    def getmessage(self):
        html = self.gethtml()
        if html:
            messages = [message for message in re.findall(r'<script>STK && STK.pageletM && STK.pageletM.view\((.*?)\)</script>', html)]
            for result in messages:
                yield result

    def main(self):
        for message in self.getmessage():
            if message.find('{"pid":"pl_weibo_direct","js":') != -1:
                html = json.loads(message)['html']
                tree_all = etree.HTML(html)
                all_message = [etree.tostring(message) for message in tree_all.xpath('//div[@action-type="feed_list_item"]')]
                print len(all_message)
                field = self.field_factory.create('zhengwen_ziduan')
                for item in all_message:
                    tree = etree.HTML(item)
                    # 本帖用户ID
                    ben_tie_yong_hu_ID = self.textxpath(tree, '//div[@class="feed_content wbcon"]/a[1]/@usercard')
                    field.set('ben_tie_yong_hu_ID', ben_tie_yong_hu_ID)

                    # 本帖用户名
                    ben_tie_yong_hu_ming = self.textxpath(tree, '//div[@class="feed_content wbcon"]/a[1]/@title')
                    field.set('ben_tie_yong_hu_ming', ben_tie_yong_hu_ming)

                    # 本帖用户微博认证
                    ben_tie_yong_hu_wei_bo_ren_zheng = self.textxpath(tree, '//div[@class="feed_content wbcon"]/a[2]/@title')
                    field.set('ben_tie_yong_hu_wei_bo_ren_zheng', ben_tie_yong_hu_wei_bo_ren_zheng)

                    # 本帖用户url
                    ben_tie_yong_hu_url = self.textxpath(tree, '//div[@class="feed_content wbcon"]/a[1]/@href')
                    field.set('ben_tie_yong_hu_url', ben_tie_yong_hu_url)

                    # 本帖内容
                    ben_tie_nei_rong = xpathutil.get_Node_text(tree, '//p[@class="comment_txt"]')
                    field.set('ben_tie_nei_rong', ben_tie_nei_rong)
                    zhuanfa_pinglun_dianzan = [self.textxpath(etree.HTML(st), '//em/text()') for st in [etree.tostring(zpz) for zpz in tree.xpath('//span[@class="line S_line1"]')[1:]]]

                    # 本帖转发数
                    ben_tie_zhuan_fa_shu = zhuanfa_pinglun_dianzan[0]
                    field.set('ben_tie_zhuan_fa_shu', ben_tie_zhuan_fa_shu)

                    # 本帖评论数
                    ben_tie_ping_lun_shu = zhuanfa_pinglun_dianzan[1]
                    field.set('ben_tie_ping_lun_shu', ben_tie_ping_lun_shu)

                    # 本帖点赞数
                    ben_tie_dian_zan_shu = zhuanfa_pinglun_dianzan[2]
                    field.set('ben_tie_dian_zan_shu', ben_tie_dian_zan_shu)

                    # 本帖url
                    ben_tie_url = self.textxpath(tree, '//div[@action-type="feed_list_item"]/@mid')
                    field.set('ben_tie_url', ben_tie_url)

                    # 本帖图片链接
                    ben_tie_tu_pian_lian_jie = self.textxpath(tree, '//ul[@class="WB_media_a WB_media_a_mn clearfix"]/li[@class="WB_pic S_bg2 bigcursor"]/img/@src')
                    field.set('ben_tie_tu_pian_lian_jie', ben_tie_tu_pian_lian_jie)

                    # 本帖发帖时间
                    ben_tie_fa_tie_shi_jian = self.textxpath(tree, '//div[@class="feed_from W_textb"]/a[1]/text()')
                    field.set('ben_tie_fa_tie_shi_jian', ben_tie_fa_tie_shi_jian)

                    # 本帖来自
                    ben_tie_lai_zi = self.textxpath(tree, '//div[@class="feed_from W_textb"]/a[2]/text()')
                    field.set('ben_tie_lai_zi', ben_tie_lai_zi)

                    # 本帖发帖地点
                    '''
                    需要判断是否是转帖
                    '''
                    zhuan_flag = tree.xpath('//div[@class="comment_info"]')
                    """
                    运行一次以后后面的变量都被赋值了，虽然没有执行后面，但始终保持赋值的结果
                    """
                    try:
                        zhuan_tree = etree.HTML(etree.tostring(zhuan_flag[0]))
                        print '非原贴'
                    except:
                        print '原贴'
                        zhuan_tree = etree.HTML('<html></html>')
                    # 转帖发帖地点

                    # 转帖用户ID
                    zhuan_tie_yong_hu_ID = self.textxpath(zhuan_tree,'//div[@node-type="feed_list_forwardContent"]/a[1]/@usercard')
                    field.set('zhuan_tie_yong_hu_ID', zhuan_tie_yong_hu_ID)

                    # 转帖用户名
                    zhuan_tie_yong_hu_ming = self.textxpath(zhuan_tree, '//div[@node-type="feed_list_forwardContent"]/a[1]/text()')
                    field.set('zhuan_tie_yong_hu_ming', zhuan_tie_yong_hu_ming)

                    # 转帖用户微博认证
                    zhuan_tie_yong_hu_wei_bo_ren_zheng = self.textxpath(zhuan_tree, '//div[@node-type="feed_list_forwardContent"]/a[2]/@title')
                    field.set('zhuan_tie_yong_hu_wei_bo_ren_zheng', zhuan_tie_yong_hu_wei_bo_ren_zheng)

                    # 转帖用户url
                    zhuan_tie_yong_hu_url = self.textxpath(zhuan_tree, '//div[@node-type="feed_list_forwardContent"]/a[1]/@href')
                    field.set('zhuan_tie_yong_hu_url', zhuan_tie_yong_hu_url)

                    # 转帖url

                    # 转帖图片链接
                    zhuan_tie_tu_pian_lian_jie = self.textxpath(zhuan_tree, '//li[@class="WB_pic S_bg2 bigcursor"]/img/@src')
                    field.set('zhuan_tie_tu_pian_lian_jie', zhuan_tie_tu_pian_lian_jie)

                    # 转帖发帖时间
                    zhuan_tie_fa_tie_shi_jian = self.textxpath(zhuan_tree, '//div[@class="feed_from W_textb"]/a[1]/text()')
                    field.set('zhuan_tie_fa_tie_shi_jian', zhuan_tie_fa_tie_shi_jian)

                    # 转帖来自
                    zhuan_tie_lai_zi = self.textxpath(zhuan_tree, '//div[@class="feed_from W_textb"]/a[2]/text()')
                    field.set('zhuan_tie_lai_zi', zhuan_tie_lai_zi)

                    # 转帖内容
                    zhuan_tie_nei_rong = self.textxpath(zhuan_tree, '//p[@class="comment_txt"]/text()')
                    field.set('zhuan_tie_nei_rong', zhuan_tie_nei_rong)

                    # 转帖转发数
                    zhuan_tie_zhuan_fa_shu = self.textxpath(zhuan_tree, '//div[@class="feed_action clearfix W_fr"]/ul/li[1]/a/span/em/text()')
                    field.set('zhuan_tie_zhuan_fa_shu', zhuan_tie_zhuan_fa_shu)

                    # 转帖评论数
                    zhuan_tie_ping_lun_shu = self.textxpath(zhuan_tree, '//div[@class="feed_action clearfix W_fr"]/ul/li[2]/a/span/em/text()')
                    field.set('zhuan_tie_ping_lun_shu', zhuan_tie_ping_lun_shu)

                    # 转帖点赞数
                    zhuan_tie_dian_zan_shu = self.textxpath(zhuan_tree, '//div[@class="feed_action clearfix W_fr"]/ul/li[3]/a/span/em/text()')
                    field.set('zhuan_tie_dian_zan_shu', zhuan_tie_dian_zan_shu)
                    field.set('id', ben_tie_url)
                    data = field.make()
                    if data:
                        print json.dumps(data, ensure_ascii=False, indent=4)

    def textxpath(self, tree, path, pos=0):
        texts = tree.xpath(path)
        if not texts:
            return None
        try:
            return map(lambda x: x.strip(), filter(lambda x: x.strip(), texts))[pos]
        except:
            return None


if __name__ == '__main__':
    zw = zhengwen()
    zw.main()

