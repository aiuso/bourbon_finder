import global_vars as g
import schedule
import navigate
import search
import time
import send


##### Bourbon to search for...

g.bourbon = 'Blant'     # Search string. Partial text >> complete search term.
g.bourbon_isAvailable = False   #Default should be false
print(f'Started searching for {g.bourbon} at {send.timestamp()}...')
print('____________\n')


##### Testing and debug

search.warehouse()
search.liquor_stores()


###### Scheduled Searches

schedule.every().day.at("10:01").do(search.liquor_stores)   # Inventory updated at 10:00 AM
schedule.every().day.at("10:15").do(search.liquor_stores)   # Second check...
schedule.every(15).minutes.do(search.warehouse)             # Warehouse inventory updated every 15 minutes.

while True:
    schedule.run_pending()
    time.sleep(1)

