import schedule
import time
from datetime import datetime

def daily_report():
    print("MerchantMind AI - Daily Business Report")
    print("Report Date:", datetime.now().strftime("%d-%m-%Y"))
    print("Daily report automation is working!")

schedule.every().day.at("09:00").do(daily_report)

print("MerchantMind AI Automation Started!")

while True:
    schedule.run_pending()
    time.sleep(60)