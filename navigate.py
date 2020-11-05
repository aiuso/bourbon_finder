from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from dotenv import load_dotenv
import global_vars as g
import time
import os

load_dotenv()
log = open("stock_log.txt", "a")

##### Urls

url = {'meckabc'   : 'https://www.meckabc.com/Products/Product-Search',
       'warehouse' : 'https://abc.nc.gov/StoresBoards/Stocks'
       }


##### Functions List

def open_browser(url):
    g.options = Options()
    g.options.binary_location = os.getenv('chrome_binary')  # chrome binary path needed here.
    g.options.add_experimental_option("excludeSwitches", ["enable-automation"])
    g.options.add_experimental_option('useAutomationExtension', False)
    g.driver = webdriver.Chrome(options=g.options) #no need to specific path, if chromedriver already in path.
    g.driver.get(url)


def liquor_store_webpage():
    open_browser(url.get('meckabc'))
    g.driver.find_element(By.ID, 'search-input').send_keys(g.bourbon + Keys.ENTER)
    time.sleep(3)
    product_name = g.driver.find_elements_by_class_name('product-location-link')

    if g.bourbon in product_name[0].text:
        g.driver.find_element(By.PARTIAL_LINK_TEXT, "Blade").click()
        time.sleep(3)
        table_rows = g.driver.find_elements(By.TAG_NAME, 'td')
        g.bourbon_isAvailable = True
        return table_rows

    else:
        g.bourbon_isAvailable = False
        pass

    print('test')



def warehouse_webpage():
    open_browser(url.get('warehouse'))
    g.product_search_box = g.driver.find_element_by_id("BrandName")
    g.product_search_box.send_keys(g.bourbon + Keys.ENTER)


def warehouse_again():
    g.product_search_box = g.driver.find_element_by_id("BrandName")
    g.product_search_box.send_keys(Keys.ENTER)


def sort_store_list(list):
    instock_locations = []
    info = []

    for each in list:
        if len(info) < 2:
            if each.text == '' or 'map' in each.text.lower():
                pass
            else:
                info.append(each.text)
        else:
            instock_locations.append(info)
            info = []

    return instock_locations
