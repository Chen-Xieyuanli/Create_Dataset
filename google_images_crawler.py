#!/usr/bin/python2.7
# coding: utf-8
# Creating dataset for Bonnet

import sys
import time  # Importing the time library to check the time of code execution
import json
import re
import os
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

# from google_images_download import google_images_download


class GoogleImages():
    '''Google image crawler
    Input: keyword, at this stage we could only search for one keyword in Google.
    Output: raw images regarding the keyword.
    '''

    def __init__(self, keyword, limit=2000, save_path="downloads", using_proxy='', threads=40):
        self.keyword = keyword
        self.limit = limit
        self.save_path = str(save_path) + "/" + keyword
        self.using_proxy = using_proxy
        self.errorCount = 0
        self.count = 0

        # for multi-threads
        self.threads = threads
        self.pool_sema = threading.BoundedSemaphore(self.threads)

    def download_extended_page(self, url, chromedriver):
        from selenium import webdriver
        from selenium.webdriver.common.keys import Keys
        if sys.version_info[0] < 3:
            reload(sys)
            sys.setdefaultencoding('utf8')
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument("--headless")

        # using proxy
        if self.using_proxy:
            proxy_server = "--proxy-server=http://" + str(self.using_proxy)
            options.add_argument(proxy_server)

        try:
            browser = webdriver.Chrome(chromedriver, chrome_options=options)
        except Exception as e:
            print("Looks like we cannot locate the path the 'chromedriver' (use the '--chromedriver' "
                  "argument to specify the path to the executable.) or google chrome browser is not "
                  "installed on your machine (exception: %s)" % e)
            sys.exit()
        browser.set_window_size(1024, 768)

        # Open the link
        print("Waiting for opening the browser...")
        browser.get(url)
        time.sleep(1)
        print("Getting you a lot of images. This may take a few moments...")
        element = browser.find_element_by_tag_name("body")

        # Scroll down
        for i in range(30):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)

        try:
            browser.find_element_by_id("smb").click()
            for i in range(50):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)  # bot id protection
        except:
            for i in range(10):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)  # bot id protection

        print("Reached end of Page.")
        time.sleep(0.5)
        source = browser.page_source  # page source

        # close the browser
        browser.close()
        return source

    # building main search URL
    def build_search_url(self, search_term):
        url = 'https://www.google.com/search?q=' +\
              quote(search_term) +\
              '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch' +\
              '&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'
        return url

    def download_image(self, image_url, dir_name, pool_sema, socket_timeout=20):
        pool_sema.acquire()
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        try:
            req = Request(image_url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko)"
                              " Chrome/24.0.1312.27 Safari/537.17"})
            try:
                # timeout time to download an image
                timeout = float(socket_timeout)

                response = urlopen(req, None, timeout)
                data = response.read()
                response.close()

                # path = dir_name + "/" + str(count) + ".jpg"
                path = dir_name + "/" + str(self.count)

                try:
                    output_file = open(path, 'wb')
                    output_file.write(data)
                    output_file.close()

                except OSError as e:
                    download_status = 'fail'
                    download_message = "OSError on an image...trying next one..." + \
                        " Error: " + str(e)

                download_status = 'success'
                download_message = "Completed GoogleImage ====> " + \
                    str(self.count)

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

    # Finding 'Next Image' from the given raw page
    def _get_next_item(self, s):
        start_line = s.find('rg_meta notranslate')
        if start_line == -1:  # If no links are found then give an error!
            end_quote = 0
            link = "no_links"
            return link, end_quote
        else:
            start_line = s.find('class="rg_meta notranslate">')
            start_object = s.find('{', start_line + 1)
            end_object = s.find('</div>', start_object + 1)
            object_raw = str(s[start_object:end_object])
            # remove escape characters based on python version
            version = (3, 0)
            cur_version = sys.version_info
            if cur_version >= version:  # python3
                try:
                    object_decode = bytes(
                        object_raw, "utf-8").decode("unicode_escape")
                    final_object = json.loads(object_decode)
                except:
                    final_object = ""
            else:  # python2
                try:
                    final_object = (json.loads(self.repair(object_raw)))
                except:
                    final_object = ""
            return final_object, end_object

    # Correcting the escape characters for python2
    def replace_with_byte(self, match):
        return chr(int(match.group(0)[1:], 8))

    def repair(self, brokenjson):
        # up to 3 digits for byte values up to FF
        invalid_escape = re.compile(r'\\[0-7]{1,3}')
        return invalid_escape.sub(self.replace_with_byte, brokenjson)

    # Format the object in readable format
    def format_object(self, object):
        formatted_object = {}
        formatted_object['image_format'] = object['ity']
        formatted_object['image_height'] = object['oh']
        formatted_object['image_width'] = object['ow']
        formatted_object['image_link'] = object['ou']
        formatted_object['image_description'] = object['pt']
        formatted_object['image_host'] = object['rh']
        formatted_object['image_source'] = object['ru']
        formatted_object['image_thumbnail_url'] = object['tu']
        return formatted_object

    # Getting all links with the help of '_images_get_next_image'
    def _get_all_items(self, page, dir_name):
        threads = []
        while self.count <= self.limit:
            object, end_content = self._get_next_item(page)
            if object == "no_links":
                break
            elif object == "":
                page = page[end_content:]
            else:
                # format the item for readability
                object = self.format_object(object)

                # download the images
                t = threading.Thread(target=self.download_image, args=(object['image_link'], dir_name, self.pool_sema))
                t.start()

                # Append all the threads in the list named 'threads'
                threads.append(t)
                page = page[end_content:]
        return threads

    def download(self):
        # building main search url
        url = self.build_search_url(self.keyword)

        # downloading pages
        raw_html = self.download_extended_page(url, "./chromedriver")

        # downloading images
        print("Starting Download...")
        threads = self._get_all_items(raw_html, self.save_path)

        # waiting for all threads finished
        for t in threads:
            t.join()

        # return the downloaded count
        return self.count


# for test
if __name__ == '__main__':
    keyword = " ".join(sys.argv[1:])
    search = GoogleImages("car")
    search.download()
