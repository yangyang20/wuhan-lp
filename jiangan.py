from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pyquery import PyQuery as pq

import re
import pymysql
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.headless = True

baseUrl='https://wuhan.newhouse.fang.com'
driver = webdriver.Chrome(options=opts)


def parsePage():
    urlOne = '/house/s/jiangan1/b91/'
    driver.get(baseUrl+urlOne)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "page")))
    html = driver.find_element_by_class_name('page').get_attribute('innerHTML')

    doc = pq(html)
    pages = doc('li.fr a')
    list=[urlOne]
    for page in pages.items():
        if 'class' not in page.html() and page.attr('href'):
            list.append(page.attr('href'))

    for url in list:
        if url:
            temp = baseUrl+url
            parseHtml(temp)

    driver.quit()

def parseHtml(url):
    print(url)
    driver = webdriver.Chrome(options=opts)
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "newhouse_loupai_list")))

    html = driver.find_element_by_id('newhouse_loupai_list').get_attribute('innerHTML')
    doc = pq(html)


    list = doc('ul li')

    for item in list.items():

        if item.attr("id") and "lp_"in item.attr("id"):
            # print(item.html())
            loupan = {}
            id = item.attr("id")
            loupan['lp_id'] = re.findall('(\d+)',id)[0]
            loupan['lp_name'] = item('div.nlcd_name a').text()
            loupan['lp_price'] = item('div.nhouse_price span').text()
            loupan['lp_address'] = item('div.address a').attr('title')
            loupan['house_type'] = item('div.house_type a')
            loupan['inSale'] = item('div.fangyuan span').text()
            loupan['fangyuan'] = item('div.fangyuan a')
            parseItem(loupan)
            # print("=================")
    driver.close()


def parseItem(item):
    temp=''
    for fangyuan in item['fangyuan'].items():
        temp+=fangyuan.text()+"-"
    item['fangyuan'] = temp[:-1]
    temp=''
    for house_type in item['house_type'].items():
        temp+=house_type.text()+'-'
    item['house_type'] = temp[:-1]
    print(item)
    insterData(item)
    # pass



def insterData(data):
    connection = pymysql.connect(host='localhost',
                                 port=3306,
                                 user='root',
                                 password='root',
                                 db='test',
                                 charset='utf8')
    # 获取游标
    cursor = connection.cursor()
    sql = f'''
             INSERT INTO `wuhan`
             (`lp_id`, `lp_name`,`lp_price`,`lp_address`,`house_type`,`inSale`,`fangyuan`) VALUES
             ('{data['lp_id']}','{data['lp_name']}','{data['lp_price']}','{data['lp_address']}','{data['house_type']}','{data['inSale']}','{data['fangyuan']}')
             '''
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == '__main__':
    parsePage()