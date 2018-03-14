import time
import pymongo
from config import *
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)
wait = WebDriverWait(browser,10)
browser.set_window_size(1120, 550)
# browser.maximize_window()


def search():
    print('正在下载')
    try:
        browser.get('http://bj.58.com/')
        inp = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#keyword')))
        sub = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#searchbtn')))
        inp.send_keys('兼职')
        sub.click()
        get_message()
    except TimeoutError:
        search()


def next_page():
    print('正在翻页:')
    try:
        sub = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'body > div.main > div.leftbar > div.pagerout > div > a.next > span')))
        sub.click()
        get_message()
    except TimeoutError:
        next_page()


def get_message():
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#infolist #top_google_ad')))
        html = browser.page_source
        doc = pq(html)
        items = doc('.maincon #infolist dl').items()
        for item in items:
            job={
                'work':item.find(' a.t').text(),
                'company':item.find('a.fl').text(),
                'salary':item.find('.w133').text(),
                'time':item.find('.w68').text()
            }
            # print(job)
            save_to_mongodb(job)
    except TimeoutError:
        get_message()


def save_to_mongodb(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到mongo数据库成功',result)
    except Exception:
        print('存储失败',result)


def main():
    search()
    while True:
        next_page()
        time.sleep(5)


if __name__ == '__main__':
    main()
