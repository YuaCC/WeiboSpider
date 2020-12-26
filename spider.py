import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import re
from pyquery import PyQuery as pq
import time

import pickle
import os

class WeiboSpider:
    def __init__(self ):
        self.weibo_cn_pub_url = 'https://weibo.cn/pub/'
        self.weibo_cn_url = 'https://weibo.cn/'
        self.weibo_com_url = 'https://weibo.com/'
        self.browser = self.build_browser()
        self.browser.implicitly_wait(10)
        self.browser.get(self.weibo_com_url)

    def build_browser(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        browser = webdriver.Chrome(options=chrome_options)
        return browser

class SearchSpider(WeiboSpider):
    def __init__(self ):
        super().__init__( )
        self.jump_to_search_page_from_index()


    def jump_to_search_page_from_index(self):
        search_button = WebDriverWait(self.browser,1).until(EC.presence_of_element_located((By.CLASS_NAME,'W_ficon.ficon_search.S_ficon')))
        search_button.click()
        keyword = 'Alen'
        input_text = WebDriverWait(self.browser,1).until(EC.presence_of_element_located((By.TAG_NAME,'input')))
        search_button = WebDriverWait(self.browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME,'s-btn-b')))
        input_text.send_keys(keyword)
        search_button.click()
        find_usr_a = WebDriverWait(self.browser, 1).until(EC.presence_of_element_located((By.LINK_TEXT, '找人')))
        find_usr_a.click()

    def search(self,key):
        input_div= WebDriverWait(self.browser,1).until(EC.presence_of_element_located((By.CLASS_NAME,'search-input')))
        input_text = WebDriverWait(input_div,1).until(EC.presence_of_element_located((By.TAG_NAME,'input')))
        search_button = WebDriverWait(self.browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME,'s-btn-b')))
        input_text.clear()
        input_text.send_keys(key)
        search_button.click()
        res =[]
        try:
            usr_divs = WebDriverWait(self.browser, 1).until(EC.presence_of_all_elements_located((By.CLASS_NAME,'card.card-user-b.s-pg16.s-brt1')))
            for usr_div in usr_divs:
                info_div = WebDriverWait(usr_div, 1).until(EC.presence_of_element_located((By.CLASS_NAME, 'info')))
                usr_name_a = WebDriverWait(info_div, 1).until(EC.presence_of_element_located((By.CLASS_NAME,'name')))
                usr_name = usr_name_a.text
                ps = WebDriverWait(info_div, 1).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'p')))
                introduce = ""
                for p in ps:
                    text = p.text
                    if text.startswith("简介："):
                        introduce=text
                fans_span =  WebDriverWait(info_div, 1).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'span')))[1]
                fans_a =  WebDriverWait(fans_span, 1).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
                fans = int(fans_a.text[:-1])*10000 if fans_a.text.endswith('万') else int(fans_a.text)
                if fans > 100:
                    print(usr_name,'粉丝 {}'.format(fans),introduce)
                res.append({
                    'usr_name':usr_name,
                    'introduce':introduce,
                    'fans':fans
                })
        except TimeoutException as e:
            print('nothing found for ',key)
            pass
        return res

    def pinyin_2_hanzi(self,pinyinList):
        from Pinyin2Hanzi import DefaultDagParams
        dagParams = DefaultDagParams()
        result = None
        for pinyin in pinyinList:
            hanzi = [l[0] for l in dagParams.get_phrase([pinyin],10000)]
            if result is None:
                result = hanzi
            else:
                result =[ a+b for a in result for b in hanzi]
        return result

    def search_pinyin(self,pinyinList):
        hanzi = self.pinyin_2_hanzi(pinyinList)
        res = []
        for hz in hanzi:
            tmp =self.search(hz)
            res.extend(tmp)
            time.sleep(2)
        return res

spider = SearchSpider( )
res = spider.search_pinyin(['pao','bu'])
with open('res.pth','w') as f:
    pickle.dump(res,f)
# spider.like_all(3937348351)
print('end')
spider.browser.close()
