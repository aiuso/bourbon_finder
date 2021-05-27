from twilio.rest import Client
import global_vars as bf
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
    bf.message_string = ''
    i = 0
    while i < len(bf.stock_locations):
        bf.message_string += f'\nThere are {bf.stock_locations[i][0]} of {bf.bourbon} at {bf.stock_locations[i][1]}'
        i += 1


def text_of_local_stock():
    format_message()
    print(f'Local Stock Available! {bf.bourbon} is in stock at ABC Stores! {timestamp()}{bf.message_string}')
    with open('stock_log.txt', 'a') as file_object:
        file_object.write(f'Local Stock Available! {bf.bourbon} is in stock at ABC Stores! {timestamp()}{bf.message_string}\n\n')

    message = sms_client.messages.create(
        to=os.getenv('phone_to'),
        from_=os.getenv('phone_from'),
        body=f"{bf.bourbon} is in stock Locally! {bf.message_string}")


def text_of_warehouse_stock():
    print(f'{bf.warehouse_stock_number} cases of {bf.bourbon} in Raleigh warehouses. Monitor local stock!'
          f' {timestamp()}.')

    with open('stock_log.txt', 'a') as file_object:
        file_object.write(f'{bf.warehouse_stock_number} cases of {bf.bourbon} in Raleigh warehouses. Monitor local stock!'
          f' {timestamp()}.\n\n')

    message = sms_client.messages.create(
        to=os.getenv('phone_to'),
        from_=os.getenv('phone_from'),
        body=f'{bf.warehouse_stock_number} cases of {bf.bourbon} in Raleigh warehouses. Monitor local stock!')

