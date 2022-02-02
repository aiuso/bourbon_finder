import global_vars as bf
import search
import schedule
import time
import send
import asyncio

def init():
    bf.bourbon = 'Blant'  # Search string. Partial text >> complete search term.
    bf.bourbon_isAvailable = False  # Default should be false
    bf.isSearching = True
    print(f'Started searching for {bf.bourbon} at {send.timestamp()}...')
    print('____________\n')


async def run():
    init()

    ###### Scheduled Searches

    schedule.every().day.at("10:01").do(search.liquor_stores)  # Inventory updated at 10:00 AM
    schedule.every().day.at("10:15").do(search.liquor_stores)  # Second check...
    schedule.every(15).minutes.do(search.warehouse)  # Warehouse inventory updated every 15 minutes.

    while bf.isSearching:
        search.warehouse()
        search.liquor_stores()
        schedule.run_pending()
        time.sleep(1)
        await asyncio.sleep(1)

    send.discord_msg('Search has ended.')
