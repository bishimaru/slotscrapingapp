from ... models import Slot,BusinessDay,PachiSlotStore, SlotTitle
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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.common.by import By
import traceback


class Command(BaseCommand):
    def handle(self, *args, **options):
      with transaction.atomic():

        print('ウィンベルイースト')
        base_url = 'https://www.p-world.co.jp/_machine/dedama.cgi?hall_id=018392&type=slot/'
        d = DesiredCapabilities.CHROME
        d['goog:loggingPrefs'] = { 'performance': 'ALL' }
        option = Options()
        # option.add_argument('--headless')
        # driver.set_page_load_timeout(20)
        # driver.implicitly_wait(10)
        driver = webdriver.Chrome(settings.CHROME_DRIVER_PATH, desired_capabilities=d, options=option)

        for i in range(7):
          try:
            driver.get(base_url)
            sleep(1)
            if driver.find_elements_by_xpath('//h1[text()="504 Gateway Time-out"]'):
                raise Exception('504 Gateway Time-out')
          except Exception as e:
            print(traceback.format_exc())
            sleep(5)
          else:
                break
        for i in range(7):
          try:
            iframe = driver.find_element_by_tag_name('iframe')
            driver.switch_to.frame(iframe)
            s = driver.page_source
            li = driver.find_elements_by_css_selector('ul.slot > li')
            slot_login = li[0].find_element_by_tag_name('a').get_attribute('href')
            # slot_login.click()
            # sleep(1)
            print(777)
            print(iframe)
            print(777)
            print(slot_login)
          except Exception as e:
            print(traceback.format_exc())
            sleep(4)
          else:
                break
        for i in range(7):
          try:
            driver.get(slot_login)
          except Exception as e:
            print(e)
            sleep(5)
          else:
                break
        # 次を読み込むボタンをおす
        # button_flag = True
        # while button_flag == True:
        #     if driver.find_elements_by_id('nextListBtn'):
        #         button = driver.find_elements_by_id('nextListBtn')[0]
        #         button.click()
        #         sleep(3)
        #         button_flag = True
        #         continue
        #     button_flag = False

        # 機種名一覧ページ
        li = driver.find_elements_by_css_selector('ul.m_list > li')
        for i in li:
            print(i.find_element_by_tag_name('h2').text)
            slot_link = i.find_element_by_tag_name('a').get_attribute('href')
            for i in range(7):
              try:
                driver.get(slot_link)
              except Exception as e:
                print(traceback.format_exc())
                sleep(5)
              else:
                    break

            # 台番号一覧ページ
            tr = driver.find_elements_by_css_selector('table > tbody > tr')
            # print('XXXXXXXXXXXXXXXXX')
            # print(tr)
            for i in tr:
                num = i.find_elements_by_tag_name('td')[1].find_element_by_tag_name('a')

                print(num.text)
                print(num.get_attribute('href'))
                for i in range(7):
                  try:
                    driver.get(num.get_attribute('href'))

                  except Exception as e:
                    print(e)
                    sleep(5)
                  else:
                        break
                # 台詳細ページ
                for i in range(7):
                  try:
                    graphs = driver.find_element_by_id('divDayGraph')
                    if graphs.find_elements_by_css_selector('img.loading_img'):
                        raise Exception('グラフイメージロード中')
                  except Exception as e:
                    print(traceback.format_exc())
                    sleep(5)
                  else:
                        break
                graph_lenge_element = graphs.find_elements_by_tag_name('path')[0].get_attribute('d')
                graph_lenge_element_list = graph_lenge_element.split(',')
                y_start = graph_lenge_element_list[1]
                y_end = graph_lenge_element_list[-1]
                y_range = int(y_end) - int(y_start)
                print(y_start)
                print(y_end)
                print(y_range)

                memori_element = graphs.find_elements_by_tag_name('text')
                cnt = 0
                for i in memori_element:
                    print('====================')
                    print(cnt)

                    print(i.get_attribute('innerHTML'))
                    cnt += 1
                print(7676)
                line_element = graphs.find_elements_by_tag_name('line')
                cnt = 0
                for i in line_element:
                    print('====================')
                    print(cnt)

                    print(i.get_attribute('y1'))
                    print(i.get_attribute('y2'))
                    cnt += 1





                # print(graphs)
                # g = graphs[0].get_attribute('d')
                # print(555)
                # all_children_by_css = graphs.get_attribute("innerHTML")
                # print(all_children_by_css)



                sleep(1000)




        login = wait.until(EC.element_to_be_clickable((By.ID, 'menulogin')))
        login.click()
        email = driver.find_element_by_id("login_email")
        while (email.is_displayed() == False):
          sleep(1)
        email.send_keys("a414510nee@yahoo.co.jp")
        password = driver.find_element_by_id("login_password")
        while (password.is_displayed() == False):
          sleep(1)
        password.send_keys("9xb3wmpc")
        send_button = wait.until(EC.element_to_be_clickable((By.ID, 'login')))
        send_button.click()
        store = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[text()="ウインベル・イースト・スロット"]')))
        for i in range(7):
          try:
            store.click()
          except Exception as e:
            print(e)
            sleep(5)
          else:
                break
        button = driver.find_element_by_class_name("accept_btn").find_element_by_tag_name('form')
        for i in range(7):
          try:
            button.click()
          except Exception as e:
            print(e)
            sleep(5)
          else:
                break

        print(driver.page_source)

        lot_num_link = driver.find_elements_by_link_text('台番号で探す')
        lot_num_link[1].click()
        wait.until(EC.presence_of_all_elements_located)
        table = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'tablesorter')))

        table_element = table.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")
        td_list = [tr.find_elements_by_tag_name("td") for tr in table_element]
        lot_num_list = []
        # ２０円スロットのリストを取得
        for td in td_list:
          slot_rate = td[2].text
          if "21.73" in slot_rate:
            lot_num = td[1].find_element_by_tag_name("a").text
            lot_num_list.append(lot_num)

        total_payout = 0
        slot_title_dict = {}
        # 台番号から詳細ページへクリックして飛ぶ
        for lot_num in lot_num_list:
          print('台番号')
          print(lot_num)
          self.new_method(driver)
          lot_num_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[text()=' + lot_num + ']')))
          # lot_num_link = driver.find_element(By.XPATH, '//a[text()=' + lot_num + ']')
          print('台番号リンク')
          print(lot_num_link)

          for i in range(7):
              try:
                print('過去の詳細を見る')
                print(i)
                driver.execute_script("arguments[0].scrollIntoView();", lot_num_link)
                print('もふもふ')
                lot_num_link.click()
                print('読みこみ')
                wait.until(EC.presence_of_all_elements_located)

                if driver.find_elements_by_id("gn_interstitial_close_icon"):
                  ad_close_icon = driver.find_element_by_id("gn_interstitial_close_icon")
                  driver.execute_script("arguments[0].scrollIntoView();", ad_close_icon)
                  ad_close_icon.click()

              except Exception as e:
                print('Error---------')
                print(e)
                sleep(4)
              else:
                break
          # 日付指定
          day = 1
          print('詳細ページ')
          print(driver.page_source)

          if day:
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'Text-UnderLine')))
            d = driver.find_elements_by_class_name("Text-UnderLine")
            driver.execute_script("arguments[0].scrollIntoView();", d[day])
            # driver.execute_script("window.scrollBy(0, 400);")
            d[day].click()
            wait.until(EC.presence_of_all_elements_located)

            if driver.find_elements_by_id("gn_interstitial_close_icon"):
              ad_close_icon = driver.find_element_by_id("gn_interstitial_close_icon")
              driver.execute_script("arguments[0].scrollIntoView();", ad_close_icon)
              ad_close_icon.click()
          print(driver.page_source)
          slot_title = driver.find_element_by_id("pachinkoTi").find_element_by_tag_name("strong").text
          number = int(lot_num)
          date = datetime.now() - timedelta(day)
          table1 = driver.find_elements_by_class_name("overviewTable")
          BB = int(table1[0].find_element_by_class_name("Text-Red").text)
          RB = int(table1[0].find_element_by_class_name("Text-Yellow").text)
          last_games = int(table1[0].find_element_by_class_name("Text-Green").text)
          table2 = driver.find_elements_by_class_name("overviewTable3")
          total_games = int(table2[0].find_elements_by_tag_name('td')[1].text)
          if total_games != 0 and BB != 0:
              bb_chance = total_games // BB
          else:
              bb_chance = None
          if total_games != 0 and RB != 0:
              rb_chance = total_games // RB
          else:
              rb_chance = None
          print('機種名' )
          print(slot_title)
          print('累計')
          print(total_games)
          print(BB)
          print(RB)
          print('宵越し')
          print(last_games)

          y_axis = driver.find_element_by_id("divDayGraph").find_elements_by_class_name("jqplot-yaxis-tick")
          y_list = []
          for i in y_axis:
            y = int(i.text)
            y_list.append(y)
          y_max = max(y_list)
          canvas = driver.find_element_by_id("divDayGraph").find_element_by_class_name("jqplot-series-canvas")
          dataURLs = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
          first_png = base64.b64decode(dataURLs)
          with open("winbell.png", 'wb') as f:
              f.write(first_png)
            # PモードをRGBモードに変更
          pil_img = Image.open("winbell.png")
          rgb = pil_img.convert("RGB")
          rgb.save("winbell.png", "JPEG")
          # opencvで座標を割り出す
          img = cv2.imread("winbell.png")
          img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
          # y軸
          y_range = img.shape[0]
          # x軸
          x_range = img.shape[1]
          print("〜〜〜X軸〜〜〜〜〜")
          print(x_range)
          print("~~~Y軸〜〜〜")
          print(y_range)
          l = [[0 for i in range(3)] for j in range(y_range * x_range)]
          x_list = []
          # グラフに当てはまる座標を取得
          for y in range(y_range):
              for x in range(x_range):
                  R, G, B = img[y, x]
                  if (100 <= R <= 255) and (55 <= G <= 145) and (35 <= B <= 85):
                      x_list.append(x)
                      l.append([y, x, img[y, x]])
          coordinate = np.asarray(l, dtype=object)
          # x軸の最大値（グラフ終点のx座標）からy座標を求める
          if(x_list != []):
              target = np.where(coordinate[:, 1] == max(x_list))
              y_axis_target = coordinate[target]
              y_axis = y_axis_target[0][0]
                # 目盛り０から最大値までの距離
              black_range = y_range / 2
              print(black_range)
                # 目盛り０の座標
              zero_axis = y_range - black_range
              z = y_max / black_range
                # 目盛り０からグラフy終点の距離
              payout = (zero_axis - y_axis) * z
              print('差枚数')
              print(payout)

          store = PachiSlotStore(pk=6)
          if BusinessDay.objects.filter(store_name=store,date=date):
              business_day = BusinessDay.objects.get(store_name=store,date=date)
          else:
              business_day = BusinessDay(store_name=store,date=date)
              business_day.save()
          Slot.objects.update_or_create(
            date=business_day,
            number=number,
            defaults={
                      "name": slot_title,
                      "bigbonus": BB,
                      "regularbonus": RB,
                      "count": total_games,
                      "bbchance": bb_chance,
                      "rbchance": rb_chance,
                      "payout": payout,
                      "lastgames": last_games,
            }
          )
          if slot_title in slot_title_dict.keys():
            slot_title_dict[slot_title] += 1
          else:
            slot_title_dict[slot_title] = 1
          print("スロット機種名")
          print(slot_title_dict)
          total_payout += payout
          print("総差枚数")
          print(total_payout)

          for i in range(3):
            try:
              back = driver.find_element_by_class_name("slot").find_elements_by_tag_name('li')[2].find_element_by_tag_name("a")
              print('戻る')
              driver.execute_script("arguments[0].scrollIntoView();", back)
              sleep(1)
              back.click()
              print('もふ')
              # 要素が全て検出できるまで待機する
              wait.until(EC.presence_of_all_elements_located)
              print('読み込み待機')
              # wait.until(EC.presence_of_all_elements_located)
              print("台番号一覧に戻る")

            except Exception as e:
              print('Error---------')
              print(e)
              sleep(10)
            else:
              break
        businessDay = BusinessDay.objects.get(store_name=store,date=date)
        businessDay.total_pay = total_payout
        businessDay.save()
        for name, num in slot_title_dict.items():
          # # 前日の機種名リストに存在しなかったら新台
          # before_day = date - timedelta(1)
          # before_business_day = BusinessDay.objects.filter(store_name=store, date=before_day)
          # if before_business_day:
          #   before_slot_titles = SlotTitle.objects.filter(date=before_business_day).values_list("name")
          #   print('昨日の機種一覧')
          #   print(before_slot_titles)
          #   if name in before_business_day:
          #     if SlotTitle.objects.filter(date=businessDay,name=name):
          #       slotTitle = SlotTitle.objects.get(date=businessDay,name=name)
          #       slotTitle.numbers = num
          #       slotTitle.memo = '新台'
          #       slotTitle.save()
          #     else:
          #       SlotTitle.objects.create(date=businessDay,name=name, numbers=num, memo="新台")
          # else:
          #   if SlotTitle.objects.filter(date=businessDay,name=name):
          #     slotTitle = SlotTitle.objects.get(date=businessDay,name=name)
          #     slotTitle.numbers = num
          #     slotTitle.save()
          #   else:
          #     SlotTitle.objects.create(date=businessDay,name=name, numbers=num)
          if SlotTitle.objects.filter(date=businessDay,name=name):
              slotTitle = SlotTitle.objects.get(date=businessDay,name=name)
              slotTitle.numbers = num
              slotTitle.save()
          else:
            SlotTitle.objects.create(date=businessDay,name=name, numbers=num)
        driver.close()

    def new_method(self, driver):
        if driver.find_elements_by_id("gn_interstitial_close_icon"):
          ad_close_icon = driver.find_element_by_id("gn_interstitial_close_icon")
          driver.execute_script("arguments[0].scrollIntoView();", ad_close_icon)
          ad_close_icon.click()



      # except IndexError as e:
      #   print(e)
      #   print(traceback.format_exc())
