from unittest.mock import MagicMock, patch

import pytest

import search


@pytest.fixture
def driver():
    d = MagicMock()
    with patch.object(search.navigate, "open_browser", return_value=d):
        yield d


LOCATIONS = [["3", "Store 1, 4706 N. Tryon St. (Blantons Single Barrel)"]]


def test_liquor_stores_in_stock_sends_alert(driver):
    with patch.object(search.navigate, "liquor_store_webpage", return_value=LOCATIONS), \
            patch.object(search.send, "text_of_local_stock") as alert, \
            patch.object(search.send, "discord_msg") as discord:
        assert search.liquor_stores("Blant") == LOCATIONS
    alert.assert_called_once_with("Blant", LOCATIONS)
    discord.assert_not_called()
    driver.quit.assert_called_once()


def test_liquor_stores_not_in_stock(driver):
    with patch.object(search.navigate, "liquor_store_webpage", return_value=[]), \
            patch.object(search.send, "text_of_local_stock") as alert, \
            patch.object(search.send, "discord_msg") as discord:
        assert search.liquor_stores("Blant") == []
    alert.assert_not_called()
    assert "not in stock Locally" in discord.call_args.args[0]


def test_availability_does_not_stick_between_searches(driver):
    # The original kept a global "available" flag that was never reset.
    with patch.object(search.send, "text_of_local_stock") as alert, \
            patch.object(search.send, "discord_msg"):
        with patch.object(search.navigate, "liquor_store_webpage", return_value=LOCATIONS):
            search.liquor_stores("Blant")
        with patch.object(search.navigate, "liquor_store_webpage", return_value=[]):
            search.liquor_stores("Blant")
    assert alert.call_count == 1


def test_lookup_error_sends_nothing(driver):
    with patch.object(search.navigate, "liquor_store_webpage", side_effect=OSError("offline")), \
            patch.object(search.send, "discord_msg") as discord:
        assert search.safe(search.liquor_stores, "Blant") is None
    discord.assert_not_called()


@pytest.mark.parametrize("page", ["liquor_store_webpage", "warehouse_webpage"])
def test_browser_closed_even_on_error(driver, page):
    job = search.liquor_stores if page == "liquor_store_webpage" else search.warehouse
    with patch.object(search.navigate, page, side_effect=RuntimeError("boom")):
        with pytest.raises(RuntimeError):
            job("Blant")
    driver.quit.assert_called_once()


@pytest.mark.parametrize("cases,alerted", [(7, True), (0, False)])
def test_warehouse(driver, cases, alerted):
    products = [{"code": "27090", "brand": "Blanton's Single Barrel", "listing": "Allocation",
                 "cases": cases, "size": ".75L"}]
    with patch.object(search.navigate, "warehouse_webpage", return_value=(cases, products)), \
            patch.object(search.send, "text_of_warehouse_stock") as alert, \
            patch.object(search.send, "discord_msg") as discord:
        assert search.warehouse("Blant") == cases
    assert alert.called is alerted
    assert discord.called is not alerted
    driver.quit.assert_called_once()


def test_safe_swallows_errors():
    def broken(_):
        raise ValueError("page changed")
    assert search.safe(broken, "Blant") is None

