import global_vars as bf
import search
import schedule
import time

def run():
    bf.bourbon_isAvailable = False  # Default should be false
    search.warehouse()
    search.liquor_stores()

    ###### Scheduled Searches

    schedule.every().day.at("10:01").do(search.liquor_stores)  # Inventory updated at 10:00 AM
    schedule.every().day.at("10:15").do(search.liquor_stores)  # Second check...
    schedule.every(15).minutes.do(search.warehouse)  # Warehouse inventory updated every 15 minutes.

    while True:
        schedule.run_pending()
        time.sleep(1)