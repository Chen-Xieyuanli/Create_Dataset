#!/usr/bin/python2.7
# coding: utf-8
# Creating dataset for Bonnet

from urllib import quote
import urllib2 as urllib
import time
import re
import os
import sys


class BaiduImages():
    '''Baidu image crawler
    Input: keyword, at this stage we could only search for one keyword in baidu.
    Output: raw images regarding the keyword.
    '''

    # Initialization with keyword, downloaded number, save path.
    # rn is the images number of one page, which is fixed 60 for baidu
    def __init__(self, keyword, count=2, save_path="downloads", rn=60, download_count=0):
        self.keyword = keyword
        self.count = count
        self.download_count = download_count
        self.save_path = str(save_path) + "/" + keyword
        self.rn = rn
        self.image_list = []
        self.totle_count = 0
        self.encode_keyword = quote(self.keyword)
        self.acJsonCount = self.get_ac_json_count()

        # use headers to pretend searching through browsers
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) " \
                          "AppleWebKit/537.36 (KHTML, like Gecko) " \
                          "Chrome/55.0.2883.95 Safari/537.36"
        self.headers = {'User-Agent': self.user_agent, "Upgrade-Insecure-Requests": 1,
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Encoding": "gzip, deflate, sdch",
                        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
                        "Cache-Control": "no-cache"}

    def download(self):
        for i in range(0, self.acJsonCount):
            url = self.get_search_url(i * self.rn)
            response = self.download_page(url).replace("\\", "")
            image_url_list = self.pick_image_urls(response)
            self.save_images(image_url_list)
        return self.totle_count

    def save_images(self, image_url_list, save_path=None):
        if save_path:
            self.save_path = save_path

        print "Already downloaded: " + str(self.totle_count + self.download_count) + " images"
        print "downloading: " + str(len(image_url_list)) + " images in: " + self.save_path

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        for image in image_url_list:
            host = self.get_url_host(image)
            self.headers["Host"] = host

            with open(self.save_path + "/%s.jpg" % (self.totle_count + self.download_count), "wb") as p:
                try:
                    req = urllib.Request(image, headers=self.headers)

                    # set the waiting time
                    img = urllib.urlopen(req, timeout=20)
                    p.write(img.read())
                    p.close()
                    self.totle_count += 1
                except Exception as e:
                    print "Exception" + str(e)
                    p.close()
                    # if os.path.exists("img/%s.jpg" % self.totle_count):
                    #     os.remove("img/%s.jpg" % self.totle_count)

        print "Already downloaded: " + str(self.totle_count + self.download_count) + " images"

    def pick_image_urls(self, response):
        reg = r'"ObjURL":"(http://img[0-9]\.imgtn.*?)"'  # 'r' for no escaping
        imgre = re.compile(reg)
        imglist = re.findall(imgre, response)
        return imglist

    def download_page(self, url):
        page = urllib.urlopen(url)
        return page.read()

    def get_search_url(self, pn):
        return "http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=result&queryWord="\
               + self.encode_keyword + "&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=0&word="\
               + self.encode_keyword + "&s=&se=&tab=&width=&height=&face=0&istype=2&qc=&nc=1&fr=&pn="\
               + str(pn) + "&rn=" + str(self.rn) + "&gsm=1000000001e&1486375820481="

    def get_url_host(self, url):
        reg = r'http://(.*?)/'
        hostre = re.compile(reg)
        host = re.findall(hostre, url)
        if len(host) > 0:
            return host[0]
        return ""

    def get_ac_json_count(self):
        a = self.count % self.rn
        c = self.count / self.rn
        if a:
            c += 1
        return c


# for test
if __name__ == '__main__':
    keyword = " ".join(sys.argv[1:])
    search = BaiduImages(keyword)
    search.download()
