from unittest.mock import MagicMock, patch

import pytest
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import navigate


def test_parse_stock_number():
    assert navigate.parse_stock_number("1,204") == 1204
    assert navigate.parse_stock_number(" 7 ") == 7
    assert navigate.parse_stock_number("n/a") == 0


class FakeMeckSite:
    """A stateful stand-in for meckabc.com's Product Search pop-up."""

    def __init__(self, products):
        # products: {name: [(store_number, bottles, address), ...]}
        self.products = products
        self.toggle_clicked = False
        self.searched = None
        self.showing = None  # product whose store list is open
        self.window = None

    # --- elements -------------------------------------------------------
    def el(self, text="", displayed=True, on_click=None, on_keys=None, children=None):
        e = MagicMock()
        e.text = text
        e.is_displayed.return_value = displayed
        e.click.side_effect = on_click or (lambda: None)
        e.send_keys.side_effect = on_keys or (lambda keys: None)
        e.find_elements.side_effect = lambda by, value: (children or {}).get(value, [])
        return e

    def _search(self, keys):
        self.searched = keys.replace(Keys.ENTER, "")

    def _open(self, name):
        self.showing = name

    def _back(self):
        self.showing = None

    def find_elements(self, by, value):
        if (by, value) == (By.ID, "search-toggle-desktop"):
            return [self.el(on_click=lambda: setattr(self, "toggle_clicked", True))]
        if (by, value) == (By.ID, "search-toggle"):
            return [self.el(displayed=False)]
        if (by, value) == (By.ID, "search-input"):
            return [self.el(displayed=self.toggle_clicked, on_keys=self._search)]
        if (by, value) == (By.ID, "product-results"):
            return [self.el()] if self.searched else []
        if (by, value) == (By.ID, "products-search-tbody"):
            return [self.el("\n".join(self.products))] if self.searched else []
        if (by, value) == (By.ID, "products-search-body"):
            return [self.el(displayed=self.showing is None)]
        if (by, value) == (By.ID, "locations-search-body"):
            return [self.el(displayed=self.showing is not None)]
        if (by, value) == navigate.PRODUCT_LINKS:
            if not self.searched or self.showing:
                return []
            return [self.el(name, on_click=lambda n=name: self._open(n)) for name in self.products]
        if (by, value) == navigate.STORE_ROWS:
            rows = [self.el(children={"th": [self.el("Store")]})]  # header-ish row, no tds
            for number, bottles, address in self.products.get(self.showing, []):
                rows.append(self.el(children={
                    "th": [self.el(str(number))],
                    "td": [self.el(str(bottles)), self.el(address), self.el("Map It")]}))
            return rows if self.showing else []
        if (by, value) == navigate.PRODUCT_TITLE:
            return [self.el(self.showing)] if self.showing else []
        if (by, value) == (By.CLASS_NAME, "location-go-back"):
            return [self.el(on_click=self._back)] if self.showing else []
        return []

    def find_element(self, by, value):
        found = self.find_elements(by, value)
        if not found:
            from selenium.common.exceptions import NoSuchElementException
            raise NoSuchElementException(value)
        return found[0]

    def set_window_size(self, w, h):
        self.window = (w, h)


def test_liquor_store_clicks_toggle_then_reads_every_store():
    site = FakeMeckSite({
        "Blantons Single Barrel": [(1, 3, "4706 N. Tryon St."), (5, 0, "2915 Wilkinson Blvd")],
        "Blantons Gold": [(3, 2, "6400 Albermarle Rd.")],
    })
    assert navigate.liquor_store_webpage(site, " Blant ") == [
        ["3", "Store 1, 4706 N. Tryon St. (Blantons Single Barrel)"],
        ["2", "Store 3, 6400 Albermarle Rd. (Blantons Gold)"],
    ]
    assert site.toggle_clicked
    assert site.searched == "Blant"
    assert site.showing is None  # went back after each product


def test_liquor_store_nothing_in_stock(monkeypatch):
    monkeypatch.setattr(navigate.config, "PAGE_TIMEOUT", 0.05)
    site = FakeMeckSite({})
    assert navigate.liquor_store_webpage(site, "Blant") == []
    assert site.searched == "Blant"


def test_liquor_store_product_with_no_stores(monkeypatch):
    monkeypatch.setattr(navigate.config, "PAGE_TIMEOUT", 0.05)
    site = FakeMeckSite({"Blantons Gold": []})
    assert navigate.liquor_store_webpage(site, "Blant") == []


def test_liquor_store_needs_three_letters():
    with pytest.raises(ValueError):
        navigate.liquor_store_webpage(FakeMeckSite({}), "Bl")


class FakeWarehousePage:
    """NC ABC warehouse page: whole-warehouse totals until a search reloads the page."""

    def __init__(self, rows, total_text, reloads=True):
        self.rows, self.total_text, self.reloads = rows, total_text, reloads
        self.searched = None
        self.box = MagicMock()
        self.box.send_keys.side_effect = self._submit
        self.old_total = MagicMock(text="Total Number of Codes: 3,197\nTotal Number of Cases: 890,658")
        self.old_total.is_enabled.return_value = True

    def _submit(self, keys):
        self.searched = keys.replace(Keys.ENTER, "")
        if self.reloads:
            self.old_total.is_enabled.side_effect = StaleElementReferenceException()

    def find_elements(self, by, value):
        if (by, value) == (By.ID, "BrandName"):
            return [self.box]
        if (by, value) == (By.XPATH, navigate.WAREHOUSE_TOTAL_XPATH):
            return [MagicMock(text=self.total_text)] if self.searched else [self.old_total]
        if (by, value) == navigate.WAREHOUSE_ROWS and self.searched:
            out = []
            for cells in self.rows:
                row = MagicMock()
                row.find_elements.return_value = [MagicMock(text=c) for c in cells]
                out.append(row)
            return out
        return []

    def find_element(self, by, value):
        return self.find_elements(by, value)[0]


BLANTON_ROWS = [
    ["19659", "Blanton's Straight From The Barrel", "Limited", "0", ".75L", "90", "Sazerac Co.", "0", "Rick Henry"],
    ["27090", "Blanton's Single Barrel", "Allocation", "1,766", ".75L", "90", "Sazerac Co.", "999999", "Rick Henry"],
]


def test_warehouse_reads_results_after_reload():
    page = FakeWarehousePage(BLANTON_ROWS, "Total Number of Codes: 2\nTotal Number of Cases: 1,766")
    total, products = navigate.warehouse_webpage(page, "Blant")
    # Must not report the whole-warehouse total (890,658) shown before the search.
    assert total == 1766
    assert page.searched == "Blant"
    page.box.clear.assert_called_once()
    assert products == [
        {"code": "19659", "brand": "Blanton's Straight From The Barrel", "listing": "Limited",
         "cases": 0, "size": ".75L"},
        {"code": "27090", "brand": "Blanton's Single Barrel", "listing": "Allocation",
         "cases": 1766, "size": ".75L"},
    ]


def test_warehouse_page_never_reloads(monkeypatch):
    monkeypatch.setattr(navigate.config, "PAGE_TIMEOUT", 0.05)
    page = FakeWarehousePage(BLANTON_ROWS, "Total Number of Cases: 5", reloads=False)
    assert navigate.warehouse_webpage(page, "Blant") == (0, [])


def test_click_falls_back_to_javascript_when_covered():
    driver, element = MagicMock(), MagicMock()
    element.click.side_effect = ElementClickInterceptedException("map in the way")
    navigate._click(driver, element)
    driver.execute_script.assert_called_once_with("arguments[0].click();", element)


def test_open_browser_sets_options(monkeypatch):
    monkeypatch.setenv("chrome_binary", "/opt/chrome")
    monkeypatch.setenv("headless", "true")
    with patch.object(navigate.webdriver, "Chrome") as chrome:
        driver = navigate.open_browser("https://example.test")
    options = chrome.call_args.kwargs["options"]
    assert options.binary_location == "/opt/chrome"
    assert "--headless=new" in options.arguments
    driver.get.assert_called_once_with("https://example.test")


def test_open_browser_without_binary(monkeypatch):
    with patch.object(navigate.webdriver, "Chrome") as chrome:
        navigate.open_browser("https://example.test")
    assert chrome.call_args.kwargs["options"].binary_location == ""
