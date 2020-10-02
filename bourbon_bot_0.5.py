import time
import send
import global_vars as g
import navigate
import schedule


##### List bourbon to search for.

g.bourbon = 'Blant'     # Search term string. Site has a hard time with complete terms
print(f'Started searching for {g.bourbon} at {send.timestamp()}...')
print('____________\n')


###### Search Functions


def search_liquor_stores():
    navigate.liquor_store_webpage()
    not_in_stock_message = g.driver.find_elements_by_id('dnn_ctr543_View_NoResults')

    if not_in_stock_message:
        print(f'{g.bourbon} is not in stock Locally. {send.timestamp()}.')
    else:
        navigate.sorted_store_list()
        send.text_of_local_stock()
    g.driver.close()


def search_warehouse():
    navigate.warehouse_webpage()
    info = g.driver.find_elements_by_xpath('/html/body/div[2]/div/div[3]/p/b[2]') # some xpaths known to change on other websites after refresh
    g.warehouse_stock_number = int(info[0].text)

    if g.warehouse_stock_number > 0:
        send.text_of_warehouse_stock()
    else:
        print(f'{g.bourbon} is not in stock at Warehouses. {send.timestamp()}.')
    g.driver.close()


###### Scheduled Searching

#search_warehouse()
#search_liquor_stores()

schedule.every().day.at("10:01").do(search_liquor_stores)
schedule.every().day.at("10:15").do(search_liquor_stores)
schedule.every(15).minutes.do(search_warehouse)

while True:
    schedule.run_pending()
    time.sleep(1)
