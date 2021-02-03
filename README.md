# Bourbon Bot


As any Bourbon fan already knows: one of the best tasting – and hardest to come by – bourbon is a nice bottle of Blanton’s. The goal of bourbon bot is to put a bottle of bourbon ~~in the hands of anyone who~~ my hands! 


# Requirements

Selenium (https://www.selenium.dev/documentation/en/webdriver/)
Twilio  (https://www.twilio.com/docs/api)
chromedriver (https://chromedriver.chromium.org/downloads)
~~BeautifulSoup4~~ Previous versions of burbon_bot attempted to implement bs4, but webpage changes have made it easier to scrape data solely using Selenium.


# What it does
* Navigates webpages using Selenium webdriver.
* Scrapes webpage data into data objects.
* Uses Twilio SMS API to send text about inventory stock and location.
* Uses Discord webhook to send Discord notifications about inventory stock and location.


# Limitations
This script only is optimized to search North Carolina state liquor inventory. Adjustments required to search/scrape other websites.
