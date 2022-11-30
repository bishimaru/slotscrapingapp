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
        base_url = 'https://daidata.goraggio.com/101014/'
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
        # 店舗TOPへ
        for i in range(7):
          try:
            driver.get(base_url)
            if driver.find_elements_by_xpath('//h1[text()="Forbidden"]'):
              raise ImportError
          except Exception as e:
            print(e)
            sleep(5)
          else:
                break
        # print(777)
        
        # 同意画面へ
        for i in range(7):
          try:
            print(777)
            accept = driver.find_element_by_css_selector('li.accept_btn > form' )
            accept.location_once_scrolled_into_view
            accept.click()
            sleep(1)
          except Exception as e:
            print(e)
            sleep(3)
          else:
                break
        # 広告のXボタンクリック
        for i in range(7):
          try:
            if driver.find_elements_by_id("gn_interstitial_close_icon"):
              ad_close_icon = driver.find_element_by_id("gn_interstitial_close_icon")
              driver.execute_script("arguments[0].scrollIntoView();", ad_close_icon)
              ad_close_icon.click()
              sleep(1)
          except Exception as e:
            print(e)
            sleep(3)
          else:
                break
        for i in range(7):
          try:
            name_list = driver.find_elements_by_css_selector('ul.pachinko > li')
            print(666)
            print(name_list)
            print(name_list[0].text)
            name_list[0].location_once_scrolled_into_view
            name_list[0].click()
            sleep(1)

          except Exception as e:
            print(e)
            sleep(3)
          else:
                break
        print(driver.page_source)

        sleep(1000)