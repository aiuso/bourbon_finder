import time
import send
import global_vars as g
import navigate
import schedule


##### Bourbon to search for...

g.bourbon = 'Blant'     # Search string. Patrial text >> complete search term.
print(f'Started searching for {g.bourbon} at {send.timestamp()}...')
print('____________\n')


###### Search Functions

def search_liquor_stores():
    navigate.liquor_store_webpage()
    not_in_stock_message = g.driver.find_elements_by_id('dnn_ctr543_View_NoResults')    # Message when 0 results return.

    if not_in_stock_message:
        print(f'{g.bourbon} is not in stock Locally. {send.timestamp()}.')
    else:
        navigate.sorted_store_list()
        send.text_of_local_stock()
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


##### Testing and debug functions

#search_warehouse()
#search_liquor_stores()


###### Scheduled Searches

schedule.every().day.at("10:01").do(search_liquor_stores)   # Inventory updated at 10:00 AM
schedule.every().day.at("10:15").do(search_liquor_stores)   # Second check...
schedule.every(15).minutes.do(search_warehouse)             # Warehouse inventory updated every 15 minutes.

while True:
    schedule.run_pending()
    time.sleep(1)
