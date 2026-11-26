# Bourbon Bot

As any Bourbon fan already knows: one of the best tasting – and hardest to come by – bourbon is a nice bottle of Blanton’s. The goal of bourbon bot is to put a bottle of bourbon in ~~the hands of anyone who~~ my hands! The 'bot' is a Python script that scrapes NC state liquor inventories and sends notifications when that sweet bottle of Blanton’s is in stock and where you can get it.

## What it does

* Uses Selenium to search [meckabc.com](https://www.meckabc.com/) (local stores): it clicks the red **Product Search** toggle, types the bourbon, then opens each product in the results to read which stores have it.
* Uses Selenium to search the [NC ABC warehouse stock page](https://abc.nc.gov/StoresBoards/Stocks).
* Prints what it finds on every check: the warehouse total plus cases per product (NC code, size, listing type), and the bottle count, store number, address and exact product for each local store.
* When stock is found, sends an alert by Twilio SMS and by Discord webhook (with `@here`), and appends it to `stock_log.txt`.
* When nothing is in stock, posts a short "not in stock" note to Discord only.
* Runs once, or keeps watching on a schedule:
  * Local stores at 10:01 and 10:15 AM (the stores update inventory at 10:00 AM).
  * The warehouse every 15 minutes.

## Requirements

* Python 3.9 or newer
* Google Chrome. Selenium 4.6+ downloads a matching chromedriver for you, so you no longer need to install it yourself.
* A Twilio account for SMS (optional)
* A Discord webhook and/or Discord bot (optional)

Install the Python packages:

```bash
pip install -r requirements.txt
```

## Configuration (.env)

Copy `.env.example` to `.env` and fill in what you use. Never commit `.env` (it is in `.gitignore`).
Any service that is not configured is skipped, so you can start with Discord only, for example.

| Variable | Required | What it is |
| --- | --- | --- |
| `SID` | For SMS | Twilio Account SID |
| `TOKEN` | For SMS | Twilio Auth Token |
| `phone_from` | For SMS | Your Twilio phone number, e.g. `+15555550100` |
| `phone_to` | For SMS | The number that receives alerts |
| `discord_webhook_url` | For Discord alerts | Webhook URL from Discord: Channel settings > Integrations > Webhooks |
| `bot_token` | For `bot.py` | Discord bot token from the Discord Developer Portal |
| `chrome_binary` | No | Path to Chrome if it is not in the default location |
| `headless` | No | `true` to run Chrome without a window |
| `bourbon` | No | Default search text (default `Blant`) |
| `log_file` | No | Where in-stock alerts are logged (default `stock_log.txt`) |

## How to run

There are three ways to start a search. All of them use the same search code in `main.py`.

**Command line**

```bash
python main.py "Blant"          # search now, then keep watching on the schedule (Ctrl+C to stop)
python main.py "Blant" --once   # search once and exit
```

**Desktop window (Tkinter)**

```bash
python gui.py
```

Type the bourbon, choose *Single search* or *Continuous*, then press **Search** (or hit Enter). **Stop** ends a continuous search. A progress bar runs while a search is going, and the **Dark mode** switch flips between the dark and light bourbon themes. The look comes from [ttkbootstrap](https://ttkbootstrap.readthedocs.io/), which `pip install -r requirements.txt` installs.

**Discord bot**

```bash
python bot.py
```

In the Discord Developer Portal, turn on **Message Content Intent** for the bot. Then use these commands in a channel the bot can read:

| Command | What it does |
| --- | --- |
| `$run [bourbon]` | Start a continuous search (uses the default if no bourbon is given) |
| `$stop` | Stop the search |
| `$status` | Show what is being searched |
| `$hello` | Check that the bot is alive |
| `$help` | List the commands |

**Tip:** partial names match more listings. `Blant` works better than `Blanton's`.

## Project layout

| File | Purpose |
| --- | --- |
| `main.py` | `BourbonSearch` runner (scheduling, start and stop) and the command line |
| `search.py` | One search of each site: open browser, scrape, notify, close browser |
| `navigate.py` | Selenium page navigation and scraping |
| `send.py` | Discord, Twilio SMS and log file notifications |
| `config.py` | Site URLs and settings from `.env` |
| `gui.py` | Desktop window (Tkinter, styled with ttkbootstrap) |
| `bot.py` | Discord bot |
| `bourbon.py` | Reference list of NC ABC product codes (not used by the search yet) |
| `tests/` | Unit tests |

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

The tests mock Selenium, Twilio and Discord. They never open a browser, visit the ABC sites, or send a text or Discord message.

## Limitations

* Only the North Carolina ABC sites (Mecklenburg stores and the state warehouse) are supported. Other sites need changes to `navigate.py`.
* Like the website, the Meck ABC search needs at least 3 letters.
* Scraping depends on the sites' current page layout. If a site changes, the selectors in `navigate.py` may need updating. For Meck ABC: `search-toggle-desktop`, `search-input`, `product-location-link`, `#product-locations-list` and `location-go-back`. For the warehouse: `BrandName` and the "Total Number of Cases" text.
* The Meck ABC results pop-up lists only products that are in stock at some store, so an empty pop-up means "not in stock".

## History

* Previous versions of bourbon_bot used BeautifulSoup4, but webpage changes made it easier to scrape data solely using Selenium.
* `bourbon_bot_0.6.py` and `global_vars.py` were replaced by `main.py` and the `BourbonSearch` class.
