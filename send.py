from twilio.rest import Client
import global_vars as g
import datetime
from dotenv import load_dotenv
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
    g.message_string = ''
    i = 0
    while i < len(g.stock_locations):
        g.message_string += f'\nThere are {g.stock_locations[i][0]} of {g.bourbon} at {g.stock_locations[i][1]}'
        i += 1


def text_of_local_stock():
    format_message()
    print(f'Local Stock Available! {g.bourbon} is in stock at ABC Stores! {timestamp()}{g.message_string}')
    with open('stock_log.txt', 'a') as file_object:
        file_object.write(f'Local Stock Available! {g.bourbon} is in stock at ABC Stores! {timestamp()}{g.message_string}\n\n')

    message = sms_client.messages.create(
        to=os.getenv('phone_to'),
        from_=os.getenv('phone_from'),
        body=f"{g.bourbon} is in stock Locally! {g.message_string}")


def text_of_warehouse_stock():
    print(f'{g.warehouse_stock_number} cases of {g.bourbon} in Raleigh warehouses. Monitor local stock!'
          f' {timestamp()}.')

    with open('stock_log.txt', 'a') as file_object:
        file_object.write(f'{g.warehouse_stock_number} cases of {g.bourbon} in Raleigh warehouses. Monitor local stock!'
          f' {timestamp()}.\n\n')

    message = sms_client.messages.create(
        to=os.getenv('phone_to'),
        from_=os.getenv('phone_from'),
        body=f'{g.warehouse_stock_number} cases of {g.bourbon} in Raleigh warehouses. Monitor local stock!')

