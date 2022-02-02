from discord_webhook import DiscordWebhook, DiscordEmbed
from twilio.rest import Client
from dotenv import load_dotenv
import global_vars as bf
import requests
import datetime
import os



##### File for Logging Stock Trends

load_dotenv()
log = open("stock_log.txt", "a")

##### Twilio

account_sid = os.getenv('SID')
auth_token = os.getenv('TOKEN')
sms_client = Client(account_sid, auth_token)


##### Function List

def timestamp():
    return datetime.datetime.now().strftime("%c")


def format_message():
    bf.message_string = ''
    i = 0
    while i < len(bf.stock_locations):
        bf.message_string += f'\nThere are {bf.stock_locations[i][0]} of {bf.bourbon} at {bf.stock_locations[i][1]}'
        i += 1


def text_of_local_stock():
    format_message()
    message = f'Local Stock Available! {bf.bourbon} is in stock at ABC Stores! {timestamp()}{bf.message_string}'
    discord_msg(message)
    write_toFile(message)
    text_message(message)


def text_of_warehouse_stock():
    message = f'{bf.warehouse_stock_number} cases of {bf.bourbon} in Raleigh warehouses. ' \
              f'Monitor local stock!'
    discord_msg(message)
    write_toFile(message)
    text_message(message)

########################  Sending Messages  ################################


##### Twilio Text Message

def write_toFile(msg):
    with open('stock_log.txt', 'a') as file_object:
        file_object.write(msg)


##### Twilio Text Message

def text_message(msg):
        message = sms_client.messages.create(
            to=os.getenv('phone_to'),
            from_=os.getenv('phone_from'),
            body=msg)


##### Discord Notifications

def discord_msg(msg):
    webhook = DiscordWebhook(url=os.getenv('discord_webhook_url'), content=msg)

    if bf.bourbon_isAvailable:
        webhook.content = '@here'
        embed = DiscordEmbed(title=f'Bourbon Updates - {timestamp()}', description=str(msg))
        webhook.add_embed(embed)
    else:
        pass

    response = webhook.execute()