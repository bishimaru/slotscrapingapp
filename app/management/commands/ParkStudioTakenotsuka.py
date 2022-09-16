from ... models import Slot,BusinessDay,PachiSlotStore
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup, NavigableString
import requests
import re
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from django.db import transaction
from django.conf import settings
import base64
from PIL import Image
import cv2
import numpy as np
from datetime import datetime, timedelta
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait

def get_data_p_arkStudioTakenotsuka():
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
          base_url = "https://p-ken.jp/p-arkst/bonus/style?ps_div=2&cost=21.7"
          
          response = requests.get(base_url)
          soup = BeautifulSoup(response.content, 'html.parser')
          titles = soup.find("ul", class_="searchUl").find_all("a", class_="list_model_nm")
          title_list = []
          for title in titles:
              title.find("span", class_="lot_cnt").extract()
              title_list.append(title.text.strip())
          store = PachiSlotStore(pk=4)
          total = 0
          date = datetime.now()
          for slot_title in title_list:
              encode_slot_title = urllib.parse.quote(slot_title, encoding='shift-jis')
              lot_numbers_list = []
              url = "https://p-ken.jp/p-arkst/bonus/lot?ps_div=2&cost=21.7&model_nm=" + encode_slot_title
              for i in range(7):
                try:
                  response = requests.get(url)
                except Exception as e:
                  print('Error---------')
                  print(e)
                else:
                  break
              soup = BeautifulSoup(response.content, 'html.parser')
              lot_numbers= soup.find_all("a", class_="select_lot_button")
              for i in lot_numbers:
                  lot_numbers_list.append(i.text)
            #   [lot_numbers_list.append(i.text) for i in lot_numbers]
              day = 1
              for lot_num in lot_numbers_list:
                  print("台番号")
                  print(lot_num)
                  url = "https://p-ken.jp/p-arkst/bonus/detail?ps_div=2&cost=21.7&model_nm=" + encode_slot_title + "&day=" + str(day) + "&lot_no=" + lot_num + "&mode="
                  driver.get(url)
                  canvas_y_max = int(driver.find_element_by_class_name("slump_graph_label").text)
                  canvas = driver.find_element_by_tag_name("canvas")
                  dataURLs = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
                  first_png = base64.b64decode(dataURLs)
                  with open("takenotsuka.png", 'wb') as f:
                      f.write(first_png)
                  # PモードをRGBモードに変更
                  pil_img = Image.open("takenotsuka.png")
                  rgb = pil_img.convert("RGB")
                  rgb.save("takenotsuka.png", "JPEG")
                  # opencvで座標を割り出す
                  img = cv2.imread("takenotsuka.png")
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
                          if (200 <= R <= 255) and (200 <= G <= 255) and (200 <= B <= 255):
                              x_list.append(x)
                              l.append([y, x, img[y, x]])
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
                              if (50 <= R <= 130) and (50 <= G <= 130) and (50 <= B <= 130):
                                  black.append(y)
                      # 目盛り０から最大値までの距離
                      black_range = (max(black) - min(black)) / 2
                      
                      # 目盛り０の座標
                      zero_axis = max(black) - black_range
                      z = canvas_y_max / black_range
                      # 目盛り０からグラフy終点の距離
                      payout = (zero_axis - y_axis) * z
                      print("差枚数")
                      print(payout)
                  else:
                      payout = 0
                  bonus_element = driver.find_element_by_class_name("bonus_summary")
                  bb = int(bonus_element.find_element_by_class_name("big").text)
                  rb = int(bonus_element.find_element_by_class_name("reg").text)
                  last_games = int(bonus_element.find_element_by_class_name("last").text)
                  total_games = int(bonus_element.find_element_by_class_name("games").text)
                  if total_games != 0 and bb != 0:
                      bb_chance = total_games // bb
                  else:
                      bb_chance = None
                  if total_games != 0 and rb != 0:
                      rb_chance = total_games // rb
                  else:
                      rb_chance = None
                  print(bb)
                  print(rb)
                  print(bb_chance)
                  print(rb_chance)
                  print(last_games)
                  print(total_games)
                  print(payout)
                  date = datetime.now() - timedelta(day)
                  print('日付')
                  print(date)
                  
                  if BusinessDay.objects.filter(store_name=store,date=date):
                      business_day = BusinessDay.objects.get(store_name=store,date=date)
                  else:
                      business_day = BusinessDay(store_name=store,date=date)
                      business_day.save()
                  Slot.objects.update_or_create(
                    date=business_day, 
                    number=int(lot_num),
                    defaults={
                              "name": slot_title,
                              "bigbonus": bb,
                              "regularbonus": rb,
                              "count": total_games,
                              "bbchance": bb_chance,
                              "rbchance": rb_chance,
                              "payout": payout,
                              "lastgames": last_games,
                    }
                  )
                  print('***総差枚数***')
                  total += int(payout)
                  print(total)       
          businessDay = BusinessDay.objects.get(store_name=store,date=date)
          businessDay.total_pay = total
          businessDay.save()
          
          driver.close()
                
