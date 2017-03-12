#!/usr/bin/env python
# coding: utf-8
# author = zerokeeper
from gevent import monkey
from gevent import Greenlet

monkey.patch_socket()
import gevent
import requests
from bs4 import BeautifulSoup
import time
import random
import re
from urllib import unquote
import optparse
import urlparse
import sys


class UCrawler(Greenlet):
    def __init__(self, query, limit):
        Greenlet.__init__(self)
        self.query = query.strip()
        self.limit = limit
        self.urls = set()

    def Geturl(self):
        try:
            gevent.joinall([
                gevent.spawn(self.BingCrawler),
                gevent.spawn(self.SoCrawler),
                gevent.spawn(self.YahooCrawler),
                gevent.spawn(self.BaiduCrawler)
            ])
            return self.urls
        except Exception, e:
            print e
            return
    def RandomHeaders(self):
        USER_AGENTS = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        ]
        random_useragent = random.choice(USER_AGENTS)
        random_x_forwarded_for = '%d.%d.%d.%d' % (random.randint(1, 254),random.randint(1, 254),random.randint(1, 254),random.randint(1, 254))
        headers = {
            'User-Agent': random_useragent,
            'X_FORWARDED_FOR': random_x_forwarded_for,
        }
        return headers


    def BingCrawler(self):
        try:
            limit = (int(self.limit) / 10)
            for page in range(limit):
                time.sleep(random.randint(1,3))
                page = page * 10 + 1
                url = "http://cn.bing.com/search?q=" + str(self.query) + "&first=" + str(page)
                r = requests.get(url, headers =self.RandomHeaders())
                content = r.content
                soup = BeautifulSoup(content, "lxml")
                tag_ol = soup.find("ol", id="b_results")
                tags_li = tag_ol.find_all("li", class_="b_algo")
                for li in tags_li:
                    url = unquote(li.a["href"])
                    print url
                    self.urls.add(url)
        except Exception, e:
            print "[Bing error]: ", e

    def SoCrawler(self):
        try:
            limit = (int(self.limit) / 10)
            for page in range(limit):
                time.sleep(random.randint(1,3))
                page = page + 1
                url = "https://www.so.com/s?q=" + str(self.query) + "&pn=" + str(page)
                r = requests.get(url, headers =self.RandomHeaders())
                content = r.content
                soup = BeautifulSoup(content, "lxml")
                tag_ul = soup.find("ul", class_="result")
                tags_li = tag_ul.find_all("li", class_="res-list")
                for li in tags_li:
                    href = li.h3.a["href"]
                    href = unquote(href)
                    if "www.so.com/link" in href:
                        url = re.match("http\://www\.so\.com/link\?url=(.*?)\&q=.*?\&ts=.*?\&t=.*?", href)
                        print url.group(1)
                        self.urls.add(url.group(1))
                    else:
                        url = href
                        print url
                        self.urls.add(url)
        except Exception, e:
            print "[So error]: ", e

    def YahooCrawler(self):
        try:
            limit = (int(self.limit) / 10)
            for page in range(limit):
                time.sleep(random.randint(1,3))
                page = page * 10 + 1
                url = "https://search.yahoo.com/search?p=" + str(self.query) + "&b=" + str(page)
                r = requests.get(url, headers =self.RandomHeaders())
                content = r.content
                soup = BeautifulSoup(content, "lxml")
                tag_div = soup.find("div", id="web")
                tags_divs = tag_div.find_all("div",class_="compTitle options-toggle")
                for div in tags_divs:
                    href = div.h3.a["href"]
                    href = unquote(href)
                    if "http://r.search.yahoo.com/_ylt=" in href:
                        url = re.search("/RO=10/RU=(.*?)/RK=0/RS=",href)
                        print url.group(1)
                        self.urls.add(url.group(1))
                    else:
                        url = href
                        print url
                        self.urls.add(url)
        except Exception, e:
            print "[Yahoo error]: ", e

    def BaiduCrawler(self):
        try:
            limit = (int(self.limit) / 10)
            for page in range(limit):
                time.sleep(random.randint(1,3))
                page = page * 10
                url = "http://www.baidu.com/s?wd=" + str(self.query) + "&pn=" + str(page) + "&tn=baidulocal"
                r = requests.get(url, headers =self.RandomHeaders())
                content = r.content
                soup = BeautifulSoup(content, "lxml")
                tag_ol = soup.find("ol")
                tags_table = tag_ol.find_all("table", border="0")
                for li in tags_table:
                    href = li.a["href"]
                    href = unquote(href)
                    url = href
                    print url
                    self.urls.add(url)
        except Exception, e:
            print "[Baidu error]: ", e

def main():
    parser = optparse.OptionParser(
        usage="usage: %prog [-q] query [--limit] number [-o] filename", version="%prog 1.0")
    parser.add_option('-q', '--query', dest='query', default=None,
                      type='string', help='The query of search engine.')
    parser.add_option('-l', '--limit', dest='limit', type='int',
                      default=20, help='The limit of each search engine.')
    parser.add_option('-o', '--output', dest='name', type='string', default=None,
                      help='If not use -o,the filename of output is time string.')
    parser.add_option('-b', '--baseurl', dest='baseurl', action='store_true', default=False,
                      help='The url of writing in file,if it is set,the url will remove path and param.')
    (options, args) = parser.parse_args()
    if options.query:
        try:
            if options.name:
                res = UCrawler(options.query, options.limit)
                print "[Starting to crawl urls]"
                urls = res.Geturl()
                print "[Writing urls in file]"
                f = open(options.name, "a")
                if options.baseurl:
                    url_list = set()
                    for url in urls:
                        url_split = urlparse.urlparse(url)
                        url = url_split.scheme + "://" + url_split.netloc
                        url_list.add(url)
                    for url in url_list:
                        f.writelines(url + "\n")
                    f.close()
                else:
                    for url in urls:
                        f.writelines(url + "\n")
                    f.close()
            else:
                name = time.strftime('%Y-%m-%d-%H:%M:%S')+".txt"
                res = UCrawler(options.query, options.limit)
                print "[Start crawling urls]"
                urls = res.Geturl()
                print "[Writing and removing duplicate urls]"
                f = open(name, "a")
                if options.baseurl:
                    url_list = set()
                    for url in urls:
                        url_split = urlparse.urlparse(url)
                        url = url_split.scheme + "://" + url_split.netloc
                        url_list.add(url)
                    for url in url_list:
                        f.writelines(url + "\n")
                    f.close()
                else:
                    for url in urls:
                        f.writelines(url + "\n")
                    f.close()
        except KeyboardInterrupt:
            print "Ctrl C - Stopping Client"
            sys.exit(1)
        except Exception, e:
            print e
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == '__main__':
    main()
