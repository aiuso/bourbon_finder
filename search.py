"""One-shot searches: open a browser, scrape, notify, close the browser."""
import logging

import config
import navigate
import send

log = logging.getLogger(__name__)


def liquor_stores(bourbon):
    """Check Mecklenburg ABC stores. Returns the list of ``[quantity, location]`` found."""
    driver = navigate.open_browser(config.URLS["meckabc"])
    try:
        locations = navigate.liquor_store_webpage(driver, bourbon)
    finally:
        driver.quit()

    print(f"\nMeck ABC stores - {bourbon} - {send.timestamp()}")
    print(send.format_locations(bourbon, locations).strip() or "  Not in stock at any store.")
    if locations:
        send.text_of_local_stock(bourbon, locations)
    else:
        send.discord_msg(f"{bourbon} is not in stock Locally. | {send.timestamp()}.")
    return locations


def warehouse(bourbon):
    """Check the NC ABC warehouse. Returns the number of cases in stock."""
    driver = navigate.open_browser(config.URLS["warehouse"])
    try:
        cases, products = navigate.warehouse_webpage(driver, bourbon)
    finally:
        driver.quit()

    print(f"\nNC ABC warehouse - {bourbon} - {send.timestamp()}")
    print(f"Total: {cases} cases{send.format_warehouse_products(products)}")
    if cases > 0:
        send.text_of_warehouse_stock(bourbon, cases, products)
    else:
        send.discord_msg(f"{bourbon} is not in stock at Warehouses. | {send.timestamp()}.")
    return cases


def safe(job, *args):
    """Run a search, logging errors instead of letting one bad page stop the loop."""
    try:
        return job(*args)
    except Exception:  # noqa: BLE001 - scraping can fail in many ways
        log.exception("%s failed", getattr(job, "__name__", job))
        return None
