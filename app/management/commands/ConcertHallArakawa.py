from django.core.management.base import BaseCommand
from ... models import Slot,BusinessDay,PachiSlotStore
import urllib.parse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep
import base64
import pytesseract
from PIL import Image
import re
import json
from django.utils import timezone
from django.db import transaction
from django.conf import settings

def get_data_ConsertHallArakawa():
    with transaction.atomic():
        # TOPページから全機種名一覧を取得
        base_url = 'https://p-ken.jp/p-charakawa/bonus/'
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        titles_ul = soup.find("ul", class_="item_list")
        titles = titles_ul.find_all('div', class_="meter")
        
        title_list = []
        for title in titles:
            title_list.append(title.contents[1].text)
        
        # 各機種名のTOPページへ遷移する
        d = DesiredCapabilities.CHROME
        d['goog:loggingPrefs'] = { 'performance': 'ALL' }
        option = Options()
        option.add_argument('--headless')
        driver = webdriver.Chrome(settings.CHROME_DRIVER_PATH, desired_capabilities=d, options=option)
        # データ一覧を全て表示する
        
        total = 0
        for slot_title in title_list:
        
            data = []
            print('機種名/' + slot_title)
            
            encode_slot_title = urllib.parse.quote(slot_title, encoding='shift-jis')
            url = base_url + 'lot?model_nm=' + encode_slot_title + '&cost=21.28&ps_div=2&mode='
            driver.get(url)
            button_flag = True
            while button_flag == True:
                buttons = driver.find_elements_by_class_name("btn-view-more")
                for button in buttons:
                    if button.text == '次を読み込み' and button.is_enabled():
                        button.click()
                        sleep(4)
                        button_flag = True
                        continue
                button_flag = False
            
            # グラフを生成するレスポンスを取得
            for entry_json in driver.get_log('performance'):
                entry = json.loads(entry_json['message'])
                if entry['message']['method'] != 'Network.requestWillBeSent' :
                    continue
                elif "getGraphs" in entry['message']['params']['request']['url']:
                    
                    # グラフurlから台番号、日付を取得
                    graph_url = entry['message']['params']['request']['url']
                    date_param = re.search(r'play_date=[0-9]{4}-[0-9]{2}-[0-9]{2}', graph_url)
                    date = re.search(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', date_param.group()).group()
                    
                    slot_number_param = re.search(r'lot_no=[0-9]+', graph_url)
                    slot_number = re.search(r'[0-9]+', slot_number_param.group()).group()
                    
                
                    # グラフデータから差枚数を取得
                    for i in range(7):
                        try:
                            response = requests.get(graph_url)
                        except requests.exceptions.ConnectionError as e:
                            print(e)
                            sleep(7)
                        else:
                            break

                    pays = re.findall(r'count\":\"-*[0-9]+', response.text)
                    final_pay = re.search(r'-*[0-9]+', pays[-1]).group()
                    final_pay = int(final_pay)
                    
                    data.append({
                        'slot_title': slot_title,
                        "date": date,
                        "slot_number": slot_number,
                        "pay": -final_pay
                    })
            data2 = []
            data_list_on = driver.find_element_by_tag_name("button")
            if data_list_on.find_element_by_tag_name('label').text == "データ表示に切り替え":
                data_list_on.click()
                sleep(4)
            rows = driver.find_element_by_id("dataTable").find_element_by_tag_name("tbody").find_elements_by_tag_name('tr')
            for row in rows:
                
                bb = int(row.find_elements_by_tag_name('td')[2].text)
                rb = int(row.find_elements_by_tag_name('td')[3].text)
                total_games = int(row.find_elements_by_tag_name('td')[4].text)
                print('BB//RB')
                print(bb)
                print(rb)

                if total_games != 0 and bb != 0:
                    bb_chance = total_games // bb
                else:
                    bb_chance = None
                if total_games != 0 and rb != 0:
                    rb_chance = total_games // rb
                else:
                    rb_chance = None

                data2.append({
                    "number": row.find_elements_by_tag_name('td')[1].text,
                    "bb": bb,
                    "rb": rb,
                    "bb_chance": bb_chance,
                    "rb_chance": rb_chance,
                    "total_games": total_games,
                })

            Store = PachiSlotStore.objects.get(pk=3)
            date = data[0]['date']
            date_format = "%Y-%m-%d"
            date_time_today = timezone.datetime.strptime(date, date_format)
            if BusinessDay.objects.filter(store_name=Store,date=date_time_today):
                    businessDay = BusinessDay.objects.get(store_name=Store,date=date)
            else:
                businessDay = BusinessDay(store_name=Store,date=date)
                businessDay.save()
            if len(data) == len(data2):  
                for idx in range(len(data)):
                    Slot.objects.update_or_create(
                        date=businessDay, 
                        number=int(data[idx]["slot_number"]),
                        defaults={
                            "name": data[idx]['slot_title'],
                            "bigbonus": data2[idx]["bb"],
                            "regularbonus":data2[idx]["rb"],
                            "count": data2[idx]["total_games"],
                            "bbchance": data2[idx]["bb_chance"],
                            "rbchance": data2[idx]["rb_chance"],
                            "payout": data[idx]['pay'],
                        }
                    )
                    total += int(data[idx]['pay'])
        businessDay = BusinessDay.objects.get(store_name=Store,date=date)
        businessDay.total_pay = total
        businessDay.save()
        driver.close()
           