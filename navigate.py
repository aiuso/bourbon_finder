"""Selenium page navigation and scraping for the NC ABC inventory sites."""
import logging
import re

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config

log = logging.getLogger(__name__)

# Paragraph on the warehouse results page, e.g. "Total Number of Cases: 766".
WAREHOUSE_TOTAL_XPATH = "//p[contains(., 'Total Number of Cases')]"
_CASES_RE = re.compile(r"Total Number of Cases:\s*([\d,]+)")


def open_browser(url):
    """Start Chrome and load ``url``. Selenium Manager finds chromedriver automatically."""
    options = Options()
    binary = config.env("chrome_binary")
    if binary:
        options.binary_location = binary
    if config.env_flag("headless"):
        options.add_argument("--headless=new")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    return driver


def _wait(driver, condition):
    return WebDriverWait(driver, config.PAGE_TIMEOUT).until(condition)


def _click(driver, element):
    """Click ``element``, falling back to a JavaScript click when something
    (like the Google map in the Meck ABC pop-up) is covering it."""
    try:
        element.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", element)


##### Local (Mecklenburg ABC) stores
#
# meckabc.com's search box is hidden until the red "Product Search" toggle is
# clicked. Results open in a pop-up that lists only products in stock somewhere;
# clicking a product shows a table of stores: number | bottles | address | Map It.

PRODUCT_LINKS = (By.CSS_SELECTOR, "#products-search-tbody .product-location-link")
STORE_ROWS = (By.CSS_SELECTOR, "#product-locations-list tr")
PRODUCT_TITLE = (By.CSS_SELECTOR, "#plu-description .plu-title")


def _open_product_search(driver):
    """Click the "Product Search" toggle (desktop or mobile layout) and return the search box."""
    for toggle_id in ("search-toggle-desktop", "search-toggle"):
        toggles = [t for t in driver.find_elements(By.ID, toggle_id) if t.is_displayed()]
        if toggles:
            toggles[0].click()
            break
    return _wait(driver, EC.visibility_of_element_located((By.ID, "search-input")))


def _read_store_rows(driver, product_name):
    # The store list loads after a short delay; wait until its title names this
    # product so we never read the previous product's stores.
    _wait(driver, EC.text_to_be_present_in_element(PRODUCT_TITLE, product_name))
    try:
        _wait(driver, lambda d: [r for r in d.find_elements(*STORE_ROWS)
                                 if r.find_elements(By.TAG_NAME, "th")])
    except TimeoutException:
        return []  # "Product is not available."
    locations = []
    for row in driver.find_elements(*STORE_ROWS):
        number = row.find_elements(By.TAG_NAME, "th")
        cells = row.find_elements(By.TAG_NAME, "td")
        if not number or len(cells) < 2:
            continue
        qty = parse_stock_number(cells[0].text)
        if qty > 0:
            place = f"Store {number[0].text.strip()}, {cells[1].text.strip()}"
            locations.append([str(qty), f"{place} ({product_name})"])
    return locations


def liquor_store_webpage(driver, bourbon):
    """Search meckabc.com for ``bourbon``.

    Returns ``[quantity, location]`` for every store that has it, where ``location``
    names the store number, address and exact product. Returns ``[]`` if none.
    """
    if len(bourbon.strip()) < 3:
        raise ValueError("The Meck ABC search needs at least 3 letters.")
    driver.set_window_size(1280, 900)  # desktop layout, so the desktop toggle is shown
    search_box = _open_product_search(driver)
    search_box.send_keys(bourbon.strip() + Keys.ENTER)

    _wait(driver, EC.visibility_of_element_located((By.ID, "product-results")))
    try:
        # Wait for "Loading..." to be replaced by results (or an empty list).
        _wait(driver, lambda d: "Loading" not in d.find_element(By.ID, "products-search-tbody").text)
    except TimeoutException:
        log.warning("Meck ABC search results did not load for %s", bourbon)
        return []

    names = [link.text.strip() for link in driver.find_elements(*PRODUCT_LINKS)]
    locations = []
    for index, name in enumerate(names):
        # Re-find the links each time; the pop-up redraws when we go back.
        _wait(driver, EC.visibility_of_element_located((By.ID, "products-search-body")))
        _click(driver, driver.find_elements(*PRODUCT_LINKS)[index])
        locations.extend(_read_store_rows(driver, name))
        _click(driver, driver.find_element(By.CLASS_NAME, "location-go-back"))
    return locations


##### State (NC ABC) warehouse

def parse_stock_number(text):
    try:
        return int(text.replace(",", "").strip())
    except (AttributeError, ValueError):
        return 0


WAREHOUSE_ROWS = (By.XPATH, "//table[.//th[contains(., 'Listing Type')]]//tbody/tr")


def warehouse_webpage(driver, bourbon):
    """Search the NC ABC warehouse page.

    Returns ``(total_cases, products)`` where each product is a dict with
    ``code``, ``brand``, ``listing``, ``cases`` and ``size``.
    """
    search_box = _wait(driver, EC.presence_of_element_located((By.ID, "BrandName")))
    # Before searching, the page already shows totals for the whole warehouse.
    # Remember that paragraph so we can tell when the results page has replaced it.
    before = driver.find_elements(By.XPATH, WAREHOUSE_TOTAL_XPATH)
    search_box.clear()
    search_box.send_keys(bourbon + Keys.ENTER)
    try:
        if before:
            _wait(driver, EC.staleness_of(before[0]))
        element = _wait(driver, EC.presence_of_element_located((By.XPATH, WAREHOUSE_TOTAL_XPATH)))
    except TimeoutException:
        log.warning("Warehouse stock count not found for %s", bourbon)
        return 0, []
    match = _CASES_RE.search(element.text)
    total = parse_stock_number(match.group(1)) if match else 0

    products = []
    for row in driver.find_elements(*WAREHOUSE_ROWS):
        cells = [c.text.strip() for c in row.find_elements(By.TAG_NAME, "td")]
        if len(cells) >= 5:
            products.append({"code": cells[0], "brand": cells[1], "listing": cells[2],
                             "cases": parse_stock_number(cells[3]), "size": cells[4]})
    return total, products
