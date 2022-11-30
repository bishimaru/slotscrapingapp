
from ... models import *
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup, NavigableString
import requests
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from django.db import transaction
from django.conf import settings
import traceback
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import base64
import re
from django.utils import timezone


class Command(BaseCommand):
    def handle(self, *args, **options):
      with transaction.atomic():
        d = DesiredCapabilities.CHROME
        d['goog:loggingPrefs'] = { 'performance': 'ALL' }
        option = Options()
        # option.add_argument('--headless')
        driver = webdriver.Chrome(settings.CHROME_DRIVER_PATH, desired_capabilities=d, options=option)
        url = "https://www.pscube.jp/h/a718762/"
        driver.implicitly_wait(5)

        # superDstation錦糸町TOPページ
        for i in range(7):
          try:
            driver.get(url)
            sleep(9)
          except Exception as e:
            print(traceback.format_exc())
          else:
                break
        # パチンコデータをクリック
        for i in range(7):
          try:
            table = driver.find_element_by_class_name("nc-main-menu")
            tr = table.find_elements_by_tag_name("tr")
            td = tr[0].find_elements_by_tag_name("td")
            href = td[1].find_element_by_tag_name("a")
            href.location_once_scrolled_into_view
            href.click()
            sleep(1)
          except Exception as e:
            print(traceback.format_exc())
          else:
              break
        # 同意画面でクリック
        for i in range(7):
          try:
            agree = driver.find_element_by_id("captcha")
            agree.location_once_scrolled_into_view
            sleep(7)
            agree.click()
            sleep(1)
          except Exception as e:
            print(traceback.format_exc())
            sleep(3)
          else:
              break

        # 大海４SPをクリック
        for i in range(7):
          try:
            target = driver.find_element_by_xpath('//div[text()="P海物語E (大海物語4SP)"]')
            target_button = target.find_element_by_xpath('..')
          
            target_button.location_once_scrolled_into_view
            target_button.click()
            sleep(1)
          except Exception as e:
            print(traceback.format_exc())
            sleep(3)
          else:
                break
        # 台番号を取得
        for i in range(7):
          try:
            tbody = driver.find_element_by_id("tblDAb")
            tr = tbody.find_elements_by_tag_name('tr')
          except Exception as e:
            print(traceback.format_exc())
          else:
                break
        # 日付を取得
        for i in range(7):
          try:
            day = driver.find_element_by_id('upYMDhms').find_element_by_tag_name("span").text
            print(day)
            day =re.search(r'(\d{4}/\d{2}/\d{2})', day).groups()
            
            print(day[0])
            date_format = "%Y/%m/%d"
            date_time_today = timezone.datetime.strptime(day[0], date_format)
            print('日付')
            print(date_time_today)
            

          except Exception as e:
              print(traceback.format_exc())
          else:
                  break
          
        num_list = []
        total_pay = 0
        for i in tr:
          num = i.find_elements_by_tag_name("td")[0].text
          num_list.append(num)
        store = PachiSlotStore.objects.get(pk=7)
        if BusinessDay.objects.filter(store_name=store,date=date_time_today):
            business_day = BusinessDay.objects.get(store_name=store,date=date_time_today)
        else:
            business_day = BusinessDay(store_name=store,date=date_time_today)
            business_day.save()
        # 取得した台番号を順番にクリック
        for num in num_list:
          for i in range(7):
            try:
              detail = driver.find_element_by_xpath('//a[text()=' + str(num) + ']')
              detail.location_once_scrolled_into_view
              detail.click()
              sleep(1)
            except Exception as e:
              print(traceback.format_exc())
              sleep(3)
            else:
                  break
          # 日付指定（1日前、2日前のみ可能）
          day = 0
          if day:
            # day = str(day)
            # driver.execute_script('document.getElementById("YMD-ul").children.item(' + day + ').classList.add("selected")')

            ul = driver.find_element_by_id('YMD-ul')
            li = ul.find_elements_by_tag_name('li')
            li[day].location_once_scrolled_into_view

            li[day].click()
            sleep(1)
          print('*********台番号***********')
          print(num)

          for i in range(7):
            try:
                # 当たり回数、総回転数を取得
              t = driver.find_element_by_id('tblDAb')
              tr = t.find_elements_by_tag_name('tr')

              td = tr[0].find_elements_by_tag_name('td')
              bonus = int(td[1].text)
              before_day_bonus1 = int(td[2].text)
              before_day_bonus2 = int(td[3].text)
              print("当たり回数")
              print(bonus)
              
              td = tr[3].find_elements_by_tag_name('td')
              total_game = int(td[1].text)
              before_total_game1 = int(td[2].text)
              before_total_game2 = int(td[3].text)
              print('総ゲーム:' + str(total_game))
              bb_chance = total_game / bonus
            except Exception as e:
              print(traceback.format_exc())
              sleep(3)
            else:
                  break

          for i in range(7):
            try:
              # グラフのエンドポイントを取得
              div = driver.find_element_by_id('svg' + str(day))
              g = div.find_elements_by_css_selector('g.amcharts-graph-line')
              c = g[1].find_elements_by_tag_name('circle')  
              # print(g[1].get_attribute('innerHTML'))
              y = c[-1].get_attribute("transform")

              graph_end_y_axis = re.search(r'((\d+),(-*\d+))', y).groups()[2]
              print('グラフ終点Y軸')
              # print(y)
              print(graph_end_y_axis)
              y = c[1].get_attribute("transform")
              graph_start_y_axis = re.search(r'((\d+),(-*\d+))', y).groups()[2]
              print('グラフ始点Y軸')
              print(graph_start_y_axis)
              if int(graph_end_y_axis) == 0:
                raise ValueError("error!")
              print('グラフ始点から終点までのY軸の距離')
              graph_y_range = int(graph_start_y_axis) - int(graph_end_y_axis)
              print(graph_y_range)

              # メモリの数を取得
              g = div.find_elements_by_tag_name('g')[1]
              # print(g.get_attribute('innerHTML'))  
              g1 = g.find_elements_by_class_name('amcharts-value-axis')[1]
            
              # print(g1.get_attribute('innerHTML'))  
              g2 = g1.find_elements_by_tag_name('g')
              
              # メモリの数
              momeri_count = len(g2)
              # print('メモリの数' + str(momeri_count))
            except Exception as e:
              print(traceback.format_exc())
              sleep(3)
            else:
                  break
        
          
          for i in range(7):
            try:
              # Y軸の長さ
              c = div.find_elements_by_tag_name("clipPath")
              y_width = c[-1].find_element_by_tag_name("rect").get_attribute("height")
              print('Y軸の長さ')
              print(y_width)
              # １メモリあたりのY軸の長さ
              one_memori = int(y_width) / momeri_count
              # print(one_memori)
              payout = (graph_y_range / one_memori) * 2500
              print('********差枚数************')
              print(payout)
              yen_payout = payout * 4
              # 時短、確変を除く通常時の回転数
              tbody = driver.find_element_by_id('tblHISTb')
              tr = tbody.find_elements_by_tag_name('tr')
            except Exception as e:
              print(traceback.format_exc())
            else:
                  break
          sleep(1000)
          right_games = 0
          bonus_in_nomal_time = 0
          for i in tr:
            if i.find_elements_by_tag_name('td')[3].text == '初当り':
              bonus_in_nomal_time += 1
            elif i.find_elements_by_tag_name('td')[3].text == '継続':
              g = i.find_elements_by_tag_name('td')[2].text
              right_games += int(g)
          print('継続' + str(right_games))
          print('初当たり' + str(bonus_in_nomal_time))
          if bonus_in_nomal_time != 0:
            print(567)
            left_games = total_game - right_games - bonus_in_nomal_time  * 100
          else:
            left_games = total_game - right_games
          print('通常G' + str(left_games))

          # 機種名取得
          for i in range(7):
            try:
             name = driver.find_element_by_id('divKI-name').text
            except Exception as e:
              print(traceback.format_exc())
              sleep(3)
            else:
                  break
                
          # 千円あたりの回転数を計算
          # 払い出し　＝　（あたり回数　＊　1500）* 4
          # 投資　＝（総回転数　/　X(１kあたり回転数））　＊　1000
          # 払い出し　ー　投資　＝　payout

          # （あたり回数　＊　6000）　ー　（総回転数　/　X(１kあたり回転数））　＊　1000　＝　payout
          # （あたり回数　＊　6000）　ー　　payout　＝ （総回転数　/　X(１kあたり回転数））　＊　1000
          # ((あたり回数　＊　6000）　ー　　payout) / 1000　＝ 総回転数　/　X(１kあたり回転数）
          # 総回転数 / (((あたり回数　＊　6000）　ー　　payout) / 1000) =  X

          # before_day_bonus2 = 30
          # before_total_game2 = 3000
          # payout = 7500
          
        
          game_1k = 1 / (((bonus * 1380) - payout ) / (left_games * 250))
          print("台番号" + str(num))
          
          print('1kあたり')
          
          print(game_1k)
          
          Pachinko.objects.update_or_create(
            date=business_day, 
            number=int(num),
            defaults={
                      "name": name,
                      "bonus": bonus,
                      "count": total_game,
                      "payout": payout,
                      "game_1k": game_1k,
                      "bbchance": bb_chance,
                    
            }
          )
          total_pay += payout

          driver.back()
          sleep(1)
          print('********次へ************')

        business_day.total_pay = total_pay
        business_day.save()
        driver.close()



        
          



        

        
      


    
     