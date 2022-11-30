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


# グラフ画像のメモリの数値を取得
def scale_number(url_img):
    img = Image.open(url_img)
    number = pytesseract.image_to_string(img)
    print(777)
    print(url_img)
    print(img)
    print(number)
    match = re.search(r'\d+', number)
    return (int)(match.group(0))

class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():

            d = DesiredCapabilities.CHROME
            d['goog:loggingPrefs'] = { 'performance': 'ALL' }
            options = Options()
            options.add_argument('--headless')
            options.add_argument("start-maximized")
            options.add_argument("disable-infobars")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(settings.CHROME_DRIVER_PATH, desired_capabilities=d, options=options)
            # driver.set_page_load_timeout(20)
            # driver.implicitly_wait(20)
            base_url = "https://minowa-uno-slot.p-moba.net/game_machine_detail.php?id="
            for slot_num in range(1,250):
                # 詳細ページ
                for i in range(7):
                      try:
                        response = requests.get(base_url + str(slot_num))
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # print(soup)

                      except Exception as e:
                        print('Error---------')
                        print(traceback.format_exc())
                        sleep(5)
                      else:
                        break
                # ２０円スロットか
                for i in range(7):
                      try:
                        frag_20yen = soup.find("div", class_="title_bar")

                        frag_20yen = frag_20yen.contents
                        # print(666)
                        # print(frag_20yen[1].text)

                      except Exception as e:
                        print('Error---------')
                        print(traceback.format_exc())
                        sleep(5)
                      else:
                        break
                day = 0
                if "20円スロット" in frag_20yen[1].text:

                    # タイトル、BB ,RB,ART,宵越し、総G
                    slot_title = frag_20yen[3].text

                    data = soup.find_all("div", id="sea01")
                    tds =data[day].find_all("td")
                    BB = tds[0].text
                    RB = tds[1].text
                    ART = tds[2].text
                    last_games = tds[3].text
                    total_games = tds[5].text
                    print('**************')
                    print(BB)
                    print(RB)
                    print(ART)
                    print(last_games)
                    print(total_games)
                    # グラフ、差枚数
                    graph_id = "0" + str(day)
                    # print('**************')
                    # print(graph_id)
                    graph_data = soup.find('div', id="graph" + graph_id)
                    get_img = graph_data.find('img').get("src")
                    img = requests.get(get_img)
                    # 保存するファイルを作成
                    path = "MinowaUno.png"
                    with open(path, 'wb') as f:
                        f.write(img.content)
                    # max_memori = scale_number("777.png")

                    str_img = Image.open('MinowaUno.png')
                    img_roi = str_img.crop((15, 10, 40, 25))
                    img_roi.save('kirinuki.png')

                    img = Image.open('kirinuki.png')
                    (width, height) = img.width*20, img.height*20

                    img_resize = img.resize((width, height))
                    print(555)
                    print(width)
                    print(height)
                    DIGITS_LOOKUP = {
                      # ( 1 , 1 , 1 , 0 , 1 , 1 , 1 ) : 0 ,
                      ( 0 , 0 , 1 , 0 , 0 ,
                        0 , 1 , 1 , 0 , 0 ,
                        1 , 0 , 1 , 0 , 0 ,
                        0 , 0 , 1 , 0 , 0 ,
                        0 , 0 , 1 , 0 , 0 ,
                        0 , 0 , 1 , 0 , 0 ,
                        0 , 0 , 1 , 0 , 0 ,
                        1 , 1 , 1 , 1 , 1 ,
                        ) : 1 ,
                      # ( 1 , 0 , 1 , 1 , 1 , 1 , 0 ) : 2 ,
                      # ( 1 , 0 , 1 , 1 , 0 , 1 , 1 ) : 3 ,
                      # ( 0 , 1 , 1 , 1 , 0 , 1 , 0 ) : 4 ,
                      # ( 1 , 1 , 0 , 1 , 0 , 1 , 1 ) : 5 ,
                      # ( 1 , 1 , 0 , 1 , 1 , 1 , 1 ) : 6 ,
                      # ( 1 , 0 , 1 , 0 , 0 , 1 , 0 ) : 7 ,
                      # ( 1 , 1 , 1 , 1 , 1 , 1 , 1 ) : 8 ,
                      # ( 1 , 1 , 1 , 1 , 0 , 1 , 1 ) : 9
                    }
                    img_resize.save("resize.png")
                    # cascade = cv2.CascadeClassifier("cv2data/haarcascade_russian_plate_number.xml")
                    im = cv2.imread('resize.png')
                    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    output = cv2.drawContours(img, contours, -1, (255, 255, 0), 5)
                    cv2.imwrite('output.png', output)


                    # contours, hierarchy = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE ) 
                    # img_disp = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                    # cv2.drawContours(img_disp, contours, -1, (0, 0, 255), 2)
                    # for contour in contours:
                    #     for point in contour:
                    #         cv2.circle(img_disp, point[0], 3, (0, 255, 0), -1)

                    # cv2.imshow("Image", gray)

# キー入力待ち(ここで画像が表示される)
                    cv2.waitKey()
                    # gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    # blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                    # edged = cv2.Canny(blurred, 50, 200, 255)
                    # cv2.imshow("img",edged )
                    # cv2.waitKey(0)
                    # cv2.destroyAllWindows()


                    # numbers = cascade.detectMultiScale(gray, 1.1, 5)

                    # blur = cv2.GaussianBlur(gray, (5, 5), 0)
                    # thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)
                    # contours = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
                    # for moji in contours:
                    #   x, y, w, h = cv2.boundingRect(moji)
                    #   if h < 20: continue
                    #   red = (0, 0, 255)
                    #   cv2.rectangle(im, (x, y), (x+w, y+h), red, 2)
                    # cv2.imwrite('re-moji.png', im)

                    # str_777 = pytesseract.image_to_string('resize.png')

                    # print(str_777)
                    break
