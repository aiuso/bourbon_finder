import global_vars as g
import schedule
import navigate
import time
import send


##### Bourbon to search for...

g.bourbon = 'Blant'     # Search string. Partial text >> complete search term.
print(f'Started searching for {g.bourbon} at {send.timestamp()}...')
print('____________\n')


###### Search Functions

def search_liquor_stores():
    stock_info = navigate.liquor_store_webpage()

    if g.bourbon_isAvailable:
        g.stock_locations = navigate.sort_store_list(stock_info)
        send.text_of_local_stock()

    else:
        print(f'{g.bourbon} is not in stock Locally. {send.timestamp()}.')

    g.driver.close()


def search_warehouse():
    navigate.warehouse_webpage()
    info = g.driver.find_elements_by_xpath('/html/body/div[2]/div/div[3]/p/b[2]')   # Points to warehouse stock text.
    g.warehouse_stock_number = int(info[0].text)                                    # Converts stock number to integer.

    if g.warehouse_stock_number > 0:
        send.text_of_warehouse_stock()
    else:
        print(f'{g.bourbon} is not in stock at Warehouses. {send.timestamp()}.')
    g.driver.close()


##### Testing and debug

#search_warehouse()
search_liquor_stores()


###### Scheduled Searches

schedule.every().day.at("10:01").do(search_liquor_stores)   # Inventory updated at 10:00 AM
schedule.every().day.at("10:15").do(search_liquor_stores)   # Second check...
schedule.every(15).minutes.do(search_warehouse)             # Warehouse inventory updated every 15 minutes.

while True:
    schedule.run_pending()
    time.sleep(1)
