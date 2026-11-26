"""Central configuration: site URLs and settings read from the environment (.env)."""
import os

from dotenv import load_dotenv

load_dotenv()

URLS = {
    "meckabc": "https://www.meckabc.com/",
    "warehouse": "https://abc.nc.gov/StoresBoards/Stocks",
}

# Seconds to wait for a page element before giving up.
PAGE_TIMEOUT = 15

# Default search string. A partial name ("Blant") matches more listings than a full one.
DEFAULT_BOURBON = os.getenv("bourbon", "Blant")

LOG_FILE = os.getenv("log_file", "stock_log.txt")


def env(name, default=None):
    """Read a setting at call time, so tests and late-loaded .env files are respected."""
    value = os.getenv(name, default)
    return value if value not in ("", None) else default


def env_flag(name, default=False):
    value = env(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")
