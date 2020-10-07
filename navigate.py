from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import global_vars as g

##### Urls

url = {'meckabc'   : 'https://www.meckabc.com/Products/Product-Search',
       'warehouse' : 'https://abc.nc.gov/StoresBoards/Stocks'
       }


##### Functions List

def open_browser(url):
    g.options = Options()
    g.options.binary_location = ""  # chrome binary path needed here.
    g.options.add_experimental_option("excludeSwitches", ["enable-automation"])
    g.options.add_experimental_option('useAutomationExtension', False)
    g.driver = webdriver.Chrome(options=g.options) #no need to specific path, if chromedriver already in path.
    g.driver.get(url)


def liquor_store_webpage():
    open_browser(url.get('meckabc'))
    product_search_box = g.driver.find_element_by_name("dnn$ctr543$View$TextBoxDescription")
    product_search_box.send_keys(g.bourbon)
    g.driver.find_element_by_id("dnn_ctr543_View_ButtonSubmit").click()


def warehouse_webpage():
    open_browser(url.get('warehouse'))
    g.product_search_box = g.driver.find_element_by_id("BrandName")
    g.product_search_box.send_keys(g.bourbon + Keys.ENTER)


def warehouse_again():
    g.product_search_box = g.driver.find_element_by_id("BrandName")
    g.product_search_box.send_keys(Keys.ENTER)


def sorted_store_list():
    g.stock_locations = []
    g.driver.find_element_by_link_text('View Locations').click()
    store_list = g.driver.find_elements_by_class_name('store')

    for store in store_list:
        store_stock = store.text.split('\n')
        g.stock_locations.append(store_stock[1:3])
