"""Notifications: Discord webhook, Twilio SMS and the local stock log."""
import datetime
import logging

from discord_webhook import DiscordEmbed, DiscordWebhook
from twilio.rest import Client

import config

log = logging.getLogger(__name__)

_sms_client = None


def timestamp():
    return datetime.datetime.now().strftime("%c")


def sms_client():
    """Create the Twilio client on first use, so importing this module needs no secrets."""
    global _sms_client
    if _sms_client is None:
        _sms_client = Client(config.env("SID"), config.env("TOKEN"))
    return _sms_client


##### Message formatting

def format_locations(bourbon, stock_locations):
    return "".join(f"\nThere are {qty} of {bourbon} at {place}" for qty, place in stock_locations)


def local_stock_message(bourbon, stock_locations):
    return (f"Local Stock Available! {bourbon} is in stock at ABC Stores! {timestamp()}"
            f"{format_locations(bourbon, stock_locations)}")


def format_warehouse_products(products):
    return "".join(f"\n{p['cases']} cases of {p['brand']} {p['size']} (NC code {p['code']}, {p['listing']})"
                   for p in products)


def warehouse_stock_message(bourbon, cases, products=()):
    return (f"{cases} cases of {bourbon} in Raleigh warehouses. Monitor local stock!"
            f"{format_warehouse_products(products)}")


##### Alerts

def alert(message):
    """Send an in-stock alert everywhere: Discord (with @here), the log file and SMS."""
    discord_msg(message, in_stock=True)
    write_to_file(message)
    text_message(message)


def text_of_local_stock(bourbon, stock_locations):
    alert(local_stock_message(bourbon, stock_locations))


def text_of_warehouse_stock(bourbon, cases, products=()):
    alert(warehouse_stock_message(bourbon, cases, products))


##### Channels

def write_to_file(msg):
    with open(config.LOG_FILE, "a", encoding="utf-8") as file_object:
        file_object.write(msg + "\n")


def text_message(msg):
    to, from_ = config.env("phone_to"), config.env("phone_from")
    if not (config.env("SID") and config.env("TOKEN") and to and from_):
        log.info("Twilio not configured; skipping SMS")
        return None
    return sms_client().messages.create(to=to, from_=from_, body=msg)


def discord_msg(msg, in_stock=False):
    url = config.env("discord_webhook_url")
    if not url:
        log.info("Discord webhook not configured; skipping: %s", msg)
        return None
    webhook = DiscordWebhook(url=url, content=msg)
    if in_stock:
        webhook.content = "@here"
        webhook.add_embed(DiscordEmbed(title=f"Bourbon Updates - {timestamp()}", description=str(msg)))
    return webhook.execute()
