from numpy import extract
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium import webdriver
from bs4 import BeautifulSoup as bs
import re as re
import numpy as np
import time
import pandas as pd


def loading(driver, dynamic_element):
    try:
        return WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, dynamic_element)))
    finally:
        driver.quit()

# PATH = 'C:\\Users\\amir\Downloads\\chromedriver_win32\\chromedriver.exe'
# USERNAME = ''
# PASSWORD = ''


# driver = webdriver.Chrome(PATH)
# driver.get("https://www.linkedin.com/uas/login")
# time.sleep(2)

# email=driver.find_element_by_id("username")
# email.send_keys(USERNAME)
# password=driver.find_element_by_id("password")
# password.send_keys(PASSWORD)
# password.send_keys(Keys.RETURN)
# time.sleep(2)

def scroll(driver):
    lastHeight = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    while True:

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        newHeight = driver.execute_script("return document.body.scrollHeight")
        time.sleep(2)
        try:
            showmore = driver.find_element_by_class_name('scaffold-finite-scroll__load-button')
            if showmore:
                showmore.click()
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                newHeight = driver.execute_script("return document.body.scrollHeight")
                time.sleep(2)

        except Exception as e:
            print(e)

        if newHeight == lastHeight:
            return True
        lastHeight = newHeight


def get_my_connection(driver):
    driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    df = pd.DataFrame(columns=['url', 'user'])
    is_done = scroll(driver)
    
    connections = driver.find_elements_by_class_name('mn-connection-card')
    for cn in connections:
        data = {'user':cn.find_element_by_class_name('mn-connection-card__name').text,'url':cn.find_element_by_class_name('mn-connection-card__picture').get_attribute('href')}
        df=df.append(data, ignore_index=True)
    df.to_csv('./amir.csv', encoding='utf-8', index=False)
    return df

#for getting your connections
# df = get_my_connection(driver)
    
def get_connection(driver, url):
    
    driver.get(url)
    tp_card = driver.find_element_by_class_name('pv-top-card--list')
    driver.get(tp_card.find_element_by_tag_name('a').get_attribute('href'))
    time.sleep(2)
    driver.find_elements_by_xpath("//*[@class='artdeco-pill artdeco-pill--slate artdeco-pill--2 artdeco-pill--choice artdeco-pill--selected ember-view search-reusables__filter-pill-button']")[1].click()
    time.sleep(2)

    driver.find_elements_by_xpath("//*[@class='artdeco-button artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view']")[0].click()
    time.sleep(2)

    driver.find_elements_by_xpath("//*[@class='artdeco-button artdeco-button--2 artdeco-button--primary ember-view ml2']")[0].click()
    time.sleep(5)
    
    connections = []
    user_connections = driver.find_elements_by_class_name('entity-result__title-text')
    scroll(driver)

    number_page = int(driver.find_elements_by_xpath("//*[@class='artdeco-pagination__pages artdeco-pagination__pages--number']/li")[-1].text)

    try:
        for page in range(number_page):
            for user in user_connections:
                time.sleep(2)
                data = {'user':user.find_element_by_tag_name('a').text.split('\n')[0],
                        'url':user.find_element_by_tag_name('a').get_attribute('href').split('?')[0]}
                connections.append(data)
            scroll(driver)
            next = driver.find_element_by_xpath('//button[@aria-label="Next"]')
            next.click()
            scroll(driver)
            time.sleep(1)
            user_connections = driver.find_elements_by_class_name('entity-result__title-text')

        df = pd.DataFrame(connections)
        df.to_csv(url.split('/')[-2] + '.csv', encoding='utf-8', index=False)

    except Exception as e:
        print('user got exceotion'+ url.split('/')[-2])
        df = pd.DataFrame(connections)
        df.to_csv(url.split('/')[-2] + '.csv', encoding='utf-8', index=False)


# amir_df = pd.read_csv('./amir.csv', encoding='utf-8')
# urls = list(amir_df['url'].values)

# for url in urls:
#     get_connection(driver,url)
import os

persons = os.listdir('./data/')
def merge_csv():
    all = []
    for p in persons:
        df = pd.read_csv('./data/'+p, encoding='utf-8')
        e2 = p.split('.csv')[0]
        urls = df['url'].values
        for url in urls:
            if url[-1] == '/':
                e1 = url.split('/')[-2]
            else:
                e1 = url.split('/')[-1]
            all.append({'e1':e1, 'e2':e2})

    df = pd.DataFrame(all)
    df.to_csv('db.csv', encoding='utf-8', index=False)


# merge_csv()


def convert_to_id(path='./db.csv'):
    df = pd.read_csv(path, encoding='utf-8')
    all_user = set(list(df['e1'].values) + list(df['e2'].values))

    dic = {}
    for idx, user in enumerate(all_user):
        dic[user] = idx
    
    for key, value in dic.items():
        # df['e1'].mask(df['e1'] == key, value, inplace=True)
        # df['e2'].mask(df['e2'] == key, value, inplace=True)
        # df['e1'] = df['e1'].mask(df['e1'] == key, value)
        # df['e2'] = df['e2'].mask(df['e2'] == key, value)
        df['e1'] = np.where((df.e1 == key),value,df.e1)
        df['e2'] = np.where((df.e2 == key),value,df.e2)

    # df = pd.DataFrame(all)
    df.to_csv('iddb.csv', encoding='utf-8', index=False, header=False)

convert_to_id()