#!/usr/bin/python2.7
# coding: utf-8
# Creating dataset for Bonnet

import re
import os
import sys
import ssl
import threading

version = (3, 0)
cur_version = sys.version_info
if cur_version >= version:  # If the Current Version of Python is 3.0 or above
    import urllib.request
    from urllib.request import Request, urlopen
    from urllib.request import URLError, HTTPError
    from urllib.parse import quote
    import http.client
    from http.client import IncompleteRead
    http.client._MAXHEADERS = 1000
else:  # If the Current Version of Python is 2.x
    import urllib2
    from urllib2 import Request, urlopen
    from urllib2 import URLError, HTTPError
    from urllib import quote
    import httplib
    from httplib import IncompleteRead
    httplib._MAXHEADERS = 1000


class BaiduImages():
    '''Baidu image crawler
    Input: keyword, at this stage we could only search for one keyword in baidu.
    Output: raw images regarding the keyword.
    '''

    # Initialization with keyword, downloaded number, save path.
    # rn is the images number of one page, which is fixed 60 for baidu
    def __init__(self, keyword, limit=2000, save_path="downloads", rn=60, download_count=0, threads=40):
        self.keyword = keyword
        self.limit = limit
        self.download_count = download_count + 1
        self.save_path = str(save_path) + "/" + keyword
        self.rn = rn
        self.image_list = []
        self.count = 0
        self.errorCount = 0
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

        # for multi-threads
        self.threads = threads
        self.pool_sema = threading.BoundedSemaphore(self.threads)

    def download(self):
        for i in range(0, self.acJsonCount):
            url = self.get_search_url(i * self.rn)
            response = self.download_page(url).replace("\\", "")
            image_url_list = self.pick_image_urls(response)
            threads = self.save_images(image_url_list)

            # waiting for all threads finished
            for t in threads:
                t.join()

        return self.count

    def download_image(self, image, pool_sema, socket_timeout=20):
        pool_sema.acquire()

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        host = self.get_url_host(image)
        self.headers["Host"] = host

        try:
            req = Request(image, headers=self.headers)
            try:
                # timeout time to download an image
                timeout = float(socket_timeout)

                response = urlopen(req, None, timeout)
                data = response.read()
                response.close()

                # path = dir_name + "/" + str(count) + ".jpg"
                path = self.save_path + "/%s" % (self.count + self.download_count)

                try:
                    output_file = open(path, 'wb')
                    output_file.write(data)
                    output_file.close()

                except OSError as e:
                    download_status = 'fail'
                    download_message = "OSError on an image...trying next one..." + \
                                       " Error: " + str(e)

                download_status = 'success'
                download_message = "Completed BaiduImage ====> " + \
                                   str(self.count + self.download_count)

            except UnicodeEncodeError as e:
                download_status = 'fail'
                download_message = "UnicodeEncodeError on an image...trying next one..." + \
                                   " Error: " + str(e)

            except URLError as e:
                download_status = 'fail'
                download_message = "URLError on an image...trying next one..." + \
                                   " Error: " + str(e)

        except HTTPError as e:  # If there is any HTTPError
            download_status = 'fail'
            download_message = "HTTPError on an image...trying next one..." + \
                               " Error: " + str(e)

        except URLError as e:
            download_status = 'fail'
            download_message = "URLError on an image...trying next one..." + \
                               " Error: " + str(e)

        except ssl.CertificateError as e:
            download_status = 'fail'
            download_message = "CertificateError on an image...trying next one..." + \
                               " Error: " + str(e)

        except IOError as e:  # If there is any IOError
            download_status = 'fail'
            download_message = "IOError on an image...trying next one..." + \
                               " Error: " + str(e)

        except IncompleteRead as e:
            download_status = 'fail'
            download_message = "IncompleteReadError on an image...trying next one..." + \
                               " Error: " + str(e)

        finally:
            print(download_status)
            print(download_message)
            if download_status == "success":
                self.count += 1
            else:
                self.errorCount += 1
            pool_sema.release()

    def save_images(self, image_url_list, save_path=None):
        if save_path:
            self.save_path = save_path

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        # contain threads
        threads = []

        for image in image_url_list:
            if self.count >= self.limit:
                return

            # download the images
            t = threading.Thread(target=self.download_image, args=(image, self.pool_sema))
            t.start()

            # Append all the threads in the list named 'threads'
            threads.append(t)

        return threads

    def pick_image_urls(self, response):
        reg = r'"ObjURL":"(http://img[0-9]\.imgtn.*?)"'  # 'r' for no escaping
        imgre = re.compile(reg)
        imglist = re.findall(imgre, response)
        return imglist

    def download_page(self, url):
        page = urlopen(url)
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
        a = self.limit % self.rn
        c = self.limit / self.rn
        if a:
            c += 1
        return c


# for test
if __name__ == '__main__':
    keyword = " ".join(sys.argv[1:])
    search = BaiduImages(keyword)
    search.download()
