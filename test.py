import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from threading import Thread
from multiprocessing import Process
import time


def click_href(url, browser):
    x = browser.click()
    if not x:
        print(url + '  ok')
    else:
        print(url + '  error...')


def get_proxy_url():
    proxyAPI_url = 'http://api3.xiguadaili.com/ip/?tid=559488590020119&num=1delay=1&protocol=https&filter=on'
    #
    r = requests.get(proxyAPI_url)
    if r.status_code != 200:
        return
    else:
        proxy = f'https://' + r.text +'/'
    return proxy


def chrome_url():
    # 获取代理

    proxy = get_proxy_url()

    options = Options()
    # options.add_argument('--headless')
    options.add_argument('--proxy-server=' + proxy)
    print('--proxy-server=' + proxy)

    browser = webdriver.Chrome(options=options,)
    browser.get('https://blog.csdn.net/littleRpl?spm=1001.2101.3001.5113')

    elements_list = browser.find_elements_by_class_name('article-item-box')

    t_list = []

    for element in elements_list:
        sub_elem = element.find_element_by_tag_name('a')
        href = sub_elem.get_attribute('href')

        # click_href(href, sub_elem)
        t = Thread(target=click_href, args=[href, sub_elem])
        t.start()
        t_list.append(t)

    [tt.join() for tt in t_list]


chrome_url()

# if __name__ == '__main__':
#
#     p_list = []
#     for i in range(10):
#         p = Process(target=chrome_url)
#         p.start()
#         p_list.append(p)
#
#     [pp.join() for pp in p_list]

