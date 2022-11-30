from ... models import *
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
from django.utils import timezone
import traceback



def get_data_p_arkStudioTakenotsuka(day):
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
          driver.set_page_load_timeout(20)
          driver.implicitly_wait(20)

        # パチンコ
        # P海物語E (大海物語4SP)
          pachinko_url = "https://p-ken.jp/p-arkst/bonus/lot?ps_div=1&cost=4&model_nm=P%8AC%95%A8%8C%EAE%20%28%91%E5%8AC%95%A8%8C%EA4SP%29"
          for i in range(7):
                try:
                  response = requests.get(pachinko_url)
                  soup = BeautifulSoup(response.content, 'html.parser')

                except Exception as e:
                  print('Error---------')
                  print(traceback.format_exc())
                  sleep(5)
                else:
                  break
          for i in range(7):
                try:
                  tr = soup.find_all("a", class_="select_lot_button")
                  detail_link_dic = {}
                  for i in tr:
                    detail_link_dic[i.text] = i.get('href')
                except Exception as e:
                  print('Error---------')
                  print(traceback.format_exc())
                  sleep(5)
                else:
                  break
          store = PachiSlotStore.objects.get(pk=4)
          total_pay_pachinko = 0
          business_day = ''
          for num, url in detail_link_dic.items():
            # 取得する日を選択

            if day:
                replace_str = "day=" + str(day)
                url = url.replace("day=0", replace_str)

            # 詳細ページへ データ取得
            for i in range(7):
                try:
                  driver.get('https:' + url)
                  print('<<<<<<url>>>>>>>')
                  print('https:' + url)
                  sleep(1)
                except Exception as e:
                    print('Error---------')
                    print(traceback.format_exc())
                    sleep(5)
                else:
                    break

            # 日付　取得
            for i in range(7):
                try:
                    date_element = driver.find_element_by_class_name("store-h1-title").find_element_by_tag_name('span').text
                    date =re.search(r'(\d{4}-\d{2}-\d{2})', date_element).groups()[0]
                    date_format = "%Y-%m-%d"
                    date = timezone.datetime.strptime(date, date_format)
                    print('日付')
                    print(date)
                    if not business_day:
                        if BusinessDay.objects.filter(store_name=store,date=date):
                            business_day = BusinessDay.objects.get(store_name=store,date=date)
                        else:
                            business_day = BusinessDay(store_name=store,date=date)
                            business_day.save()
                except Exception as e:
                    print('Error---------')
                    print(traceback.format_exc())
                    sleep(5)
                else:
                    break
            # 大当たり回数
            for i in range(7):
                try:
                  bonus = int(driver.find_element_by_css_selector('span.bonus').text)
                  print('当たり=' + str(bonus))
                except Exception as e:
                    print('Error---------')
                    print(traceback.format_exc())
                    sleep(5)
                else:
                    break
            # 総回転
            for i in range(7):
                try:
                  games = int(driver.find_element_by_css_selector('span.games').text)
                  print('総回転=' + str(games))
                except Exception as e:
                    print('Error---------')
                    print(traceback.format_exc())
                    sleep(5)
                else:
                    break
             # 最終ゲーム
            for i in range(7):
                try:
                  last = int(driver.find_element_by_css_selector('span.last').text)
                  print('最終G=' + str(last))
                except Exception as e:
                    print('Error---------')
                    print(traceback.format_exc())
                    sleep(5)
                else:
                    break
            # グラフ解析　差枚数　
            for i in range(7):
                try:
                    canvas_y_memori = driver.find_elements_by_class_name("slump_graph_label")
                    canvas_y_max = int(canvas_y_memori[0].text)
                    canvas_y_min = -int(canvas_y_memori[0].text)
                    print(canvas_y_max)
                    print(canvas_y_min)

                    canvas = driver.find_element_by_tag_name("canvas")
                    dataURLs = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
                    first_png = base64.b64decode(dataURLs)
                    with open("takepachi.png", 'wb') as f:
                        f.write(first_png)
                    # PモードをRGBモードに変更
                    pil_img = Image.open("takepachi.png")
                    rgb = pil_img.convert("RGB")
                    rgb.save("takepachi.png", "JPEG")
                    # opencvで座標を割り出す
                    img = cv2.imread("takepachi.png")
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
                                if (80 <= R <= 140) and (80 <= G <= 140) and (80 <= B <= 140):
                                    black.append(y)
                        # 目盛り０から最大値までの距離
                        print('メモリの最小Y軸')
                        print(min(black))
                        print('メモリの最大Y軸')
                        print(max(black))

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

                except Exception as e:
                    print('Error---------')
                    print(traceback.format_exc())
                    sleep(5)
                else:
                    break
            # 千円あたりの回転数を計算
            # 払い出し　＝　（あたり回数　＊　1400）* 4
            # 投資　＝（総回転数　/　X(１kあたり回転数））　＊　1000
            # 払い出し　ー　投資　＝　payout

            # （あたり回数　＊　6000）　ー　（総回転数　/　X(１kあたり回転数））　＊　1000　＝　payout
            # （あたり回数　＊　6000）　ー　　payout　＝ （総回転数　/　X(１kあたり回転数））　＊　1000
            # ((あたり回数　＊　6000）　ー　　payout) / 1000　＝ 総回転数　/　X(１kあたり回転数）
            # 総回転数 / (((あたり回数　＊　6000）　ー　　payout) / 1000) =  X

            # before_day_bonus2 = 30
            # before_total_game2 = 3000
            # payout = 7500
            get_bonus_count = 0
            right_games = 0
            left_games = 0
            tr_list = []
            table = driver.find_elements_by_css_selector('table.bonus_history > tbody > tr')
            print('trの数')
            print(len(table))
            [tr_list.append(i) for i in table]
            for i in tr_list:
                if i.find_elements_by_tag_name('td'):
                    td = i.find_elements_by_tag_name('td')
                    print(td[2].text)
                    if td[2].text == '初当たり':
                        left_games += int(td[1].text)
                        get_bonus_count += 1

                    elif td[2].text == '確変':
                        right_games += int(td[1].text)
            print(games - last - left_games - right_games - (get_bonus_count * 120))
            mohu = games - last - left_games - right_games - (get_bonus_count * 120)
            if get_bonus_count:
                nomal_games = left_games + last - mohu
            else:
                nomal_games = last - mohu
            print('台番号')
            number = num
            print(number)
            # print('通常G= ' + str(left_games))
            # print('右打ちG= ' + str(right_games))

            print('通常G')
            print(left_games + last)
            if games:
                game_1k = 1 / (((bonus * 1380 - (right_games * 0.1)) - payout ) / ((nomal_games - mohu) * 250))
            else:
                game_1k = 0
            print('1kあたり')
            print(game_1k)

            Pachinko.objects.update_or_create(
              date=business_day,
              number=number,
              defaults={
                        "name": "P海物語E (大海物語4SP)",
                        "bonus": bonus,
                        "count": games,
                        "payout": payout,
                        "game_1k": game_1k,
              }
            )
            total_pay_pachinko += payout

          businessDay = BusinessDay.objects.get(store_name=store,date=date)
          businessDay.total_pay_pachinko = total_pay_pachinko
          businessDay.save()

# ******************************スロット********************************
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
                  sleep(10)
                else:
                  break
              soup = BeautifulSoup(response.content, 'html.parser')
              lot_numbers= soup.find_all("a", class_="select_lot_button")
              for i in lot_numbers:
                  lot_numbers_list.append(i.text)
            #   [lot_numbers_list.append(i.text) for i in lot_numbers]
              day = 0
              for lot_num in lot_numbers_list:
                  print("台番号")
                  print(lot_num)
                  url = "https://p-ken.jp/p-arkst/bonus/detail?ps_div=2&cost=21.7&model_nm=" + encode_slot_title + "&day=" + str(day) + "&lot_no=" + lot_num + "&mode="
                  for i in range(7):
                        try:
                            driver.get(url)
                            canvas_y_max = int(driver.find_element_by_class_name("slump_graph_label").text)
                            canvas = driver.find_element_by_tag_name("canvas")
                        except Exception as e:
                            print(e)
                            sleep(20)
                        else:
                            break
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
                  for i in range(7):
                        try:
                            date_element = driver.find_element_by_class_name("store-h1-title").find_element_by_tag_name('span').text
                            date =re.search(r'(\d{4}-\d{2}-\d{2})', date_element).groups()[0]
                            date_format = "%Y-%m-%d"
                            date = timezone.datetime.strptime(date, date_format)
                            print('日付')
                            print(date)
                        except Exception as e:
                            print(e)
                            sleep(3)
                        else:
                            break


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
