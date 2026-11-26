"""Search runner shared by the CLI, the Tkinter GUI and the Discord bot.

Usage:  python main.py "Blanton"          # search continuously
        python main.py "Blanton" --once   # search once and exit
"""
import argparse
import asyncio
import logging

import schedule

import config
import search
import send

log = logging.getLogger(__name__)


class BourbonSearch:
    """Searches for one bourbon on a schedule until ``stop()`` is called."""

    def __init__(self, bourbon=None):
        self.bourbon = bourbon or config.DEFAULT_BOURBON
        self.is_searching = False
        self.scheduler = schedule.Scheduler()

    def search_once(self):
        search.safe(search.warehouse, self.bourbon)
        search.safe(search.liquor_stores, self.bourbon)

    def _schedule_jobs(self):
        self.scheduler.clear()
        # Store inventory is updated at 10:00 AM; check just after and once more.
        self.scheduler.every().day.at("10:01").do(search.safe, search.liquor_stores, self.bourbon)
        self.scheduler.every().day.at("10:15").do(search.safe, search.liquor_stores, self.bourbon)
        # Warehouse inventory is updated every 15 minutes.
        self.scheduler.every(15).minutes.do(search.safe, search.warehouse, self.bourbon)

    async def run(self, continuous=True, poll_seconds=1):
        """Search now, then (if ``continuous``) keep running scheduled searches.

        Blocking Selenium work runs in a worker thread so the asyncio loop
        (and the Discord bot) stays responsive.
        """
        self.is_searching = True
        print(f"Started searching for {self.bourbon} at {send.timestamp()}...")
        print("____________\n")
        await asyncio.to_thread(self.search_once)

        if continuous:
            self._schedule_jobs()
            while self.is_searching:
                await asyncio.to_thread(self.scheduler.run_pending)
                await asyncio.sleep(poll_seconds)
            self.scheduler.clear()
            send.discord_msg("Search has ended.")
        self.is_searching = False

    def stop(self):
        self.is_searching = False


def main(argv=None):
    parser = argparse.ArgumentParser(description="Watch NC ABC inventory for a bourbon.")
    parser.add_argument("bourbon", nargs="?", default=config.DEFAULT_BOURBON,
                        help="search text; partial names match more listings (default: %(default)s)")
    parser.add_argument("--once", action="store_true", help="search once and exit")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    runner = BourbonSearch(args.bourbon)
    try:
        asyncio.run(runner.run(continuous=not args.once))
    except KeyboardInterrupt:
        runner.stop()


if __name__ == "__main__":
    main()
