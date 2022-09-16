
from .ConcertHallArakawa import get_data_ConsertHallArakawa
from .ParkStudioTakenotsuka import get_data_p_arkStudioTakenotsuka
from .BBstationNippori import get_data_BBstationNippori
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date




def scraping():
    print('実行')
    get_data_p_arkStudioTakenotsuka()
    get_data_ConsertHallArakawa()
    get_data_BBstationNippori()

def start():
  scheduler = BackgroundScheduler()
  scheduler.add_job(scraping, 'cron', hour=22, minute=55)
  # scheduler.add_job(scraping, 'interval', minutes=1)
  scheduler.start()


# 5分おきに実行
# scheduler.add_job(periodic_execution, 'interval', minutes=5)

# # 1時間5秒おきに実行
# scheduler.add_job(periodic_execution, 'interval', hours=1, seconds=5)

# # 1日おきに実行
# scheduler.add_job(periodic_execution, 'interval', days=1)

# # 1週間おきに実行
# scheduler.add_job(periodic_execution, 'interval', weeks=1)

# # 2022年4月1日19時〜20時の間、1分おきに実行
# scheduler.add_job(periodic_execution, 'interval', minutes=1,
#     start_date="2022-04-01 19:00:00",
#     end_date="2022-04-01 20:00:00")

# # 毎時20分に実行
# scheduler.add_job(periodic_execution, 'cron', minute=20)

# # 月曜から金曜の間、22時になると実行
# scheduler.add_job(periodic_execution, 'cron', hour=22, day_of_week='mon-fri')
