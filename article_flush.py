import sys
import json
import time
import urllib3
import hashlib
import requests
import random

from redis import StrictRedis

from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from threading import Thread
from multiprocessing import Process

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
rc = StrictRedis(host='127.0.0.1', port='6380',)
article_set_key = 'article_hrefs'

proxy_agent = 'free'
# proxy_agent = 'xdali'

def make_proxy_from_xdali():

    _version = sys.version_info

    is_python3 = (_version[0] == 3)

    orderno = "ZF202011236319vDqRo1"
    secret = "2342494cc2b44a3ca09469513c771225"

    ip = "forward.xdaili.cn"
    port = "80"

    ip_port = ip + ":" + port

    timestamp = str(int(time.time()))
    string = ""
    string = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp

    if is_python3:
        string = string.encode()

    md5_string = hashlib.md5(string).hexdigest()
    sign = md5_string.upper()
    #print(sign)
    auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp

    #print(auth)
    proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
    headers = {"Proxy-Authorization": auth, "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"}

    value = {'proxy': proxy, 'headers': headers}
    rc.set('proxy', json.dumps(value), ex=10)
    return value

def get_proxy_from_xdali():
    proxy_info = rc.get('proxy')

    if proxy_info:
        proxy_dict = json.loads(proxy_info)
    else:
        proxy_dict = make_proxy_from_xdali()
        print('get proxy from web ...')

    return proxy_dict


def make_proxy_from_free():
    proxy = requests.get('http://127.0.0.1:5010/get').json().get('proxy', None)
    if not proxy:
        return
    delete_proxy_from_free(proxy)

    proxy_info = {"http": "http://{}".format(proxy)}
    return proxy_info


def delete_proxy_from_free(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def get_user_agent():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36"
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:22.0) Gecko/20130328 Firefox/22.0"
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36"
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36"
        "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36"
        "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36"
        "Mozilla/5.0 (Windows NT 5.0; rv:21.0) Gecko/20100101 Firefox/21.0"
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36"
        "Opera/9.80 (Windows NT 5.1; U; cs) Presto/2.7.62 Version/11.01"
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36"
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20130331 Firefox/21.0"
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36"
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36"
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36"
        "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F"
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
    ]
    headers = {"user-agent": random.choice(user_agent_list)}
    return headers


def get_articles_info():
    article_info_set = rc.smembers(article_set_key)
    if article_info_set:
        article_info_list = [json.loads(i.decode()) for i in article_info_set]
        print('get articles info from redis...')
    else:
        article_info_list = parse_articles_info()
        print('get articles info from web parse...')

    return article_info_list


def parse_articles_info():
    article_set_key = 'article_hrefs'

    options = Options()
    options.add_argument('--headless')
    # options.add_argument('--proxy-server=' + proxy)

    browser = webdriver.Chrome(options=options,)
    browser.get('https://blog.csdn.net/littleRpl?spm=1001.2101.3001.5113')

    elements_list = browser.find_elements_by_class_name('article-item-box')

    article_info_list = []
    rc.delete(article_set_key)
    for element in elements_list:
        sub_elem = element.find_element_by_tag_name('a')

        read_num = element.find_element_by_class_name('read-num').text
        href = sub_elem.get_attribute('href')
        title = sub_elem.text

        article_info = {'title': title, 'href': href}
        article_info_list.append(article_info)

        rc.sadd(article_set_key, json.dumps(article_info))

    rc.expire(article_set_key, 4*60*60)  # 1 hour expire

    return article_info_list


def get_read_count(text):
    html = etree.HTML(text, etree.HTMLParser())
    try:
        read_count = html.xpath('//span[@class="read-count"]')[0].text
    except:
        read_count = '-'

    return read_count


def read_article(article, proxy_or_agent=None):
    url = article['href']
    title = article['title']

    if proxy_or_agent == 'free':
        proxy = make_proxy_from_free()
        headers = get_user_agent()
    elif proxy_or_agent == 'xdali':
        proxy_dict = make_proxy_from_xdali()
        proxy = proxy_dict['proxy']
        headers = proxy_dict['headers']
    elif proxy_or_agent is None:
        print(f'{title}, no proxy or agent, return back...')
        return
    else:
        proxy = proxy_or_agent
        headers = get_user_agent()


    try:
        r = requests.get(url, headers=headers, proxies=proxy, verify=False, allow_redirects=False, timeout=10)
    except:
        print(f'\t\t title: {title}, proxy access failed...')
        return
    else:
        r.encoding = 'utf8'

    if r.status_code == 200:
        read_num = get_read_count(r.text)
        print(f'title: {title}, access ok, read_num: {int(read_num)+1}')
        return

    if r.status_code == 302 or r.status_code == 301:
        loc = r.headers['Location']

        r = requests.get(loc, headers=headers, proxies=proxy, verify=False, allow_redirects=False)
        r.encoding = 'utf8'
        if r.status_code != 200:
            print(f'\t\t title: {title}, proxy access failed...')
            return

        else:
            read_num = get_read_count(r.text)
            print(f'title: {title}, read_num: {read_num}')


def access_all_articles():

    articles_info_list = get_articles_info()

    while True:
        t0 = time.time()
        t_list = []
        # proxy = make_proxy_from_free()
        # print(proxy)
        for articles_info in articles_info_list:
            t = Thread(target=read_article, args=[articles_info, 'free'])
            t.start()

            t_list.append(t)

        [t.join() for t in t_list]

        t1 = time.time() - t0
        print(f'---------------- seconds: {t1} ---------------\n')
        time.sleep(3)


def mutil():
    for i in range(8):
        p = Process(target=access_all_articles)
        p.start()


if __name__ == '__main__':
    # mutil()
    # x = make_proxy_from_free()
    # print(x)
    access_all_articles()