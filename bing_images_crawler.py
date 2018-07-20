#!/usr/bin/python2.7
# coding: utf-8
# Creating dataset for Bonnet

import os
import sys
import re
import threading
import time
import ssl
import cv2

version = (3, 0)
cur_version = sys.version_info
if cur_version >= version:  # If the Current Version of Python is 3.0 or above
    import urllib.request
    from urllib.request import Request, urlopen
    from urllib.request import URLError, HTTPError
    from urllib.parse import quote
    import http.client
    import urllib
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


class BingImages():
    '''Bing image crawler
    Input: keyword, at this stage we could only search for one keyword in Bing.
    Output: raw images regarding the keyword.
    '''

    def __init__(self, keyword, limit=2000, save_path="downloads", using_proxy=False, download_count=0, threads=40):
        self.keyword = keyword
        self.limit = limit
        self.save_path = str(save_path) + "/" + keyword
        self.using_proxy = using_proxy
        self.count = 0
        self.errorCount = 0
        self.download_count = download_count + 1

        self.url_header = {"User-Agent": "Mozilla/5.0 (X11; Linux i686)"
                                          " AppleWebKit/537.17 (KHTML, like Gecko)"
                                          " Chrome/24.0.1312.27 Safari/537.17"}

        # for multi-threads
        self.threads_num = threads
        self.pool_sema = threading.BoundedSemaphore(self.threads_num)
        self.threads = []

    def download_image(self, pool_sema, image_url):
        pool_sema.acquire()
        save_path = self.save_path
        socket_timeout = 20

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        try:
            req = Request(image_url, headers=self.url_header)
            try:
                # timeout time to download an image
                timeout = float(socket_timeout)
                response = urlopen(req, None, timeout)
                data = response.read()
                response.close()

                # path = save_path + "/" + str(self.count) + ".jpg"
                path = save_path + "/" + str(self.count+self.download_count)

                try:
                    output_file = open(path, 'wb')
                    output_file.write(data)
                    output_file.close()
                    image = cv2.imread(path)
                    if not image.shape:
                        print("This image is broken!!!")

                except OSError as e:
                    download_status = 'fail'
                    download_message = "OSError on an image...trying next one..." + \
                        " Error: " + str(e)

                download_status = 'success'
                download_message = "Completed BingImage ====> " + \
                    str(self.count+self.download_count)

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

    def fetch_images_from_keyword(self, pool_sema, keyword, limit):
        current = 0
        last = ''
        threads = []  # contain threads
        while True:
            request_url = 'https://www.bing.com/images/async?q=' + quote(keyword) + '&first=' + str(current) + '&count=35&adlt=off' + '&qft='
            request = Request(request_url, None, headers=self.url_header)
            response = urlopen(request)
            html = response.read().decode('utf8')
            links = re.findall('murl&quot;:&quot;(.*?)&quot;',html)
            try:
                if links[-1] == last:
                    return
                for index, link in enumerate(links):
                    if limit is not None and current + index >= limit:
                        return
                    t = threading.Thread(target = self.download_image,args = (pool_sema, link))
                    t.start()

                    # Append all the threads in the list named 'threads'
                    self.threads.append(t)

                    current += 1
                last = links[-1]
            except IndexError:
                print('No search results for "{0}"'.format(keyword))
                return
            time.sleep(0.1)

    def download(self):
        self.fetch_images_from_keyword(self.pool_sema, self.keyword, self.limit)

        # waiting for all threads finished
        for t in self.threads:
            t.join()

        return self.count


# for test
if __name__ == "__main__":
    keyword = " ".join(sys.argv[1:])
    search = BingImages(keyword)
    search.download()
