from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from dotenv import load_dotenv
import global_vars as bf
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
    bf.options = Options()
    bf.options.binary_location = os.getenv('chrome_binary')  # chrome binary path needed here.
    bf.options.add_experimental_option("excludeSwitches", ["enable-automation"])
    bf.options.add_experimental_option('useAutomationExtension', False)
    bf.driver = webdriver.Chrome(options=bf.options) #no need to specific path, if chromedriver already in path.
    bf.driver.get(url)


def liquor_store_webpage():
    open_browser(url.get('meckabc'))
    bf.driver.find_element(By.ID, 'search-input').send_keys(bf.bourbon + Keys.ENTER)
    time.sleep(3)
    product_name = bf.driver.find_elements_by_class_name('product-location-link')
    try:
        if bf.bourbon in product_name[0].text:
            bf.driver.find_element(By.PARTIAL_LINK_TEXT, "Blade").click()
            time.sleep(3)
            table_rows = bf.driver.find_elements(By.TAG_NAME, 'td')
            bf.bourbon_isAvailable = True
            return table_rows
        else:
            bf.bourbon_isAvailable = False

    except IndexError:
        bf.bourbon_isAvailable = False



def warehouse_webpage():
    open_browser(url.get('warehouse'))
    bf.product_search_box = bf.driver.find_element_by_id("BrandName")
    bf.product_search_box.send_keys(bf.bourbon + Keys.ENTER)


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
