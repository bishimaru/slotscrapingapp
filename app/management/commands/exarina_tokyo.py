from django.core.management.base import BaseCommand

import csv
import urllib
import urllib.request
import urllib.error
from urllib import request
import requests
from bs4 import BeautifulSoup
import ssl
import datetime
# import pandas as pd
import io
import sys
import re
import pytesseract
from PIL import Image
import cv2
import tempfile
import os.path
import numpy as np
from requests import models
from ... models import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from django.db import transaction
from django.conf import settings
import traceback
from time import sleep



# 引数にグラフ画像を入れて目盛りの数値を取得
def scale_number(url_img):
    img = Image.open(url_img)
    number = pytesseract.image_to_string(img)
    match = re.search(r'\d+', number)
    return (int)(match.group(0))

# 機種名、BB、RB、前日G,総回転数、BB確率、RB確率、合成確立を辞書型で返す
def get_data(soup):
    list = {}

    # get_name = soup.find_all("h1")
    name = soup.find('p', class_='c-machine-title__title').text
    print('機種名')
    print(name)
    list["name"] = name

    get_data = soup.find_all("div", class_="c-data-slot__item-images")
    # get_data[0]=今日, get_data[1]=昨日
    get_BBdata = get_data[0].find_all("img")
    for i in get_BBdata:
        get_img = i.get("src")
        print('もふ')
        print('https://x-arena.p-moba.net/' + get_img)
        img = requests.get('https://x-arena.p-moba.net/' + get_img)
        # 保存するファイルを作成
        path = "memori.png"
        with open(path, 'wb') as f:
            f.write(img.content)
        BB = scale_number(path)

        print(BB)

    get_td = get_data.find_all("td")

    list["BB"] = (int)(get_td[0].text)
    list["RB"] = (int)(get_td[1].text)
    list["lastgame"] = (int)(get_td[2].text)
    list["totalgame"] = (int)(get_td[4].text)
    list["BBchance"] = (get_td[5].text.strip())
    list["RBchance"] = (get_td[6].text.strip())
    list["totalchance"] = (get_td[7].text.strip())
    return list


# Webからグラフ画像をで読み込んで差枚数を割り出す
def get_graph_img(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # グラフ画像を特定する(graph00=今日, graph01=昨日)
    get_graph = soup.find("div", id="graph00")
    get_img = get_graph.find("img").get("src")
    # グラフ画像を開く
    img = requests.get(get_img)

    # 保存するファイルを作成
    path = "test.png"
    with open(path, 'wb') as f:
        f.write(img.content)
    max_memori = scale_number(path)
    # PモードをRGBモードに変更
    pil_img = Image.open(path)
    rgb = pil_img.convert("RGB")
    rgb.save(path, "JPEG")
    # opencvで座標を割り出す
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # y軸
    y_range = img.shape[0]
    # x軸
    x_range = img.shape[1]

    l = [[0 for i in range(3)] for j in range(y_range * x_range)]
    x_list = []
    # グラフに当てはまる座標を取得
    for y in range(y_range):
        for x in range(x_range):
            R, G, B = img[y, x]
            if (130 <= R <= 230) and (35 <= G <= 119) and (90 <= B <= 145):
                x_list.append(x)
                l.append([y, x, img[y, x]])
    print('~~~x_list~~~~')
    print(x_list)

    coordinate = np.asarray(l, dtype=object)
    # x軸の最大値（グラフ終点のx座標）からy座標を求める
    if(x_list != []):
        target = np.where(coordinate[:, 1] == max(x_list))
        y_axis_target = coordinate[target]
        y_axis = y_axis_target[0][0]

        black = []
        # 目盛りに当てはまる座標を取得
        for y in range(y_range):
            for x in range(x_range):
                R, G, B = img[y, x]
                if (0 <= R <= 25) and (0 <= G <= 25) and (0 <= B <= 25):
                    black.append(y)
        # 目盛り０から最大値までの距離
        black_range = (max(black) - min(black)) / 2
        # 目盛り０の座標
        zero_axis = max(black) - black_range

        z = max_memori / black_range
        # 目盛り０からグラフy終点の距離
        payout = (zero_axis - y_axis) * z

        os.remove(path)
        return (int)(payout)
    else:
        return (int)(0)

def accept(driver):
    if driver.find_elements_by_xpath('//p[text()="利用規約に同意する"]'):
        for i in range(7):
              try:
                driver.find_element_by_id('terms_btn').click()
                sleep(1)
              except Exception as e:
                print('Error---------')
                print(traceback.format_exc())
                sleep(5)
              else:
                break


# R 130-230 G 35-119 B 95-145

class Command(BaseCommand):

    def handle(self, *args, **options):

        d = DesiredCapabilities.CHROME
        d['goog:loggingPrefs'] = { 'performance': 'ALL' }
        options = Options()
        # options.add_argument('--headless')
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(settings.CHROME_DRIVER_PATH, desired_capabilities=d, options=options)
        # driver.set_page_load_timeout(20)
        # driver.implicitly_wait(20)

        for i in range(7):
              try:
                driver.get('https://x-arena.p-moba.net/game.php')
              except Exception as e:
                print('Error---------')
                print(traceback.format_exc())
                sleep(5)
              else:
                break
        accept(driver)

        total = 0
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        for i in range(650, 1200):

            # urlを取得
            url = 'https://x-arena.p-moba.net/game_machine_detail.php?id=' + \
                str(i)
            # タイトルを取得（２０円スロットが含まれているか確認）
            for i in range(7):
                  try:
                    driver.get(url)
                    driver.page_source
                  except Exception as e:
                    print('Error---------')
                    print(traceback.format_exc())
                    sleep(5)
                  else:
                    break
            accept(driver)
            # response = requests.get(driver.page_source)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            title = soup.find("span", class_="c-machine-number__category")
            title = title.text
            print(666)
            print(title)

            if("20円スロット" in title):
                target = '番台'
                idx = title.find(target)
                nb = title[:idx]

                data = {}
                data = get_data(soup)
                data["number"] = nb
                payout = get_graph_img(url)
                data['payout'] = payout
                total += payout

                d = SlotData(
                    store_name='エクスアリーナ東京',
                    name=data['name'],
                    number=data['number'],
                    date=now,
                    bigbonus=data['BB'],
                    regularbonus=data['RB'],
                    count=data['totalgame'],
                    bbchance=data['BBchance'],
                    rbchance=data['RBchance'],
                    totalchance=data['totalchance'],
                    lastgames=data['lastgame'],
                    payout=data['payout'],
                )
                d.save()
        p = TotalPay(
            store_name='エクスアリーナ東京',
            date=now,
            totalpay=total
        )
        p.save()
        # url_img = 'screen.png'
        # img = Image.open(
        #     '/Users/yamamotokenta/Desktop/myprojectdir/list/sample666.gif')
        # number = pytesseract.image_to_string(img)
        # match = re.search(r'\d+', number)
        # print(match.group(0))
