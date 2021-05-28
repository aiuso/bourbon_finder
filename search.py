import global_vars as bf
import navigate
import send

###### Search Functions

def liquor_stores():
    stock_info = navigate.liquor_store_webpage()

    if bf.bourbon_isAvailable:
        bf.stock_locations = navigate.sort_store_list(stock_info)
        send.text_of_local_stock()
    else:
        print(f'{bf.bourbon} is not in stock Locally. {send.timestamp()}.')

    bf.driver.close()


def warehouse():
    navigate.warehouse_webpage()
    info = bf.driver.find_elements_by_xpath('/html/body/div[2]/div/div[3]/p/b[2]')   # Points to warehouse stock text.
    bf.warehouse_stock_number = int(info[0].text)                                    # Converts stock number to integer.

    if bf.warehouse_stock_number > 0:
        send.text_of_warehouse_stock()
    else:
        print(f'{bf.bourbon} is not in stock at Warehouses. {send.timestamp()}.')

    bf.driver.close()