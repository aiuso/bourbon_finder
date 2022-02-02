from dotenv import load_dotenv
import global_vars as bf
import discord
import requests
import asyncio
import main
import os

load_dotenv()
client = discord.Client()
bot = os.getenv('bot_token')

############ Bot Keywords
search = '$run'
help = '$help'
bourbon = '$bourbon'


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$run'):
        await message.channel.send('Search has started...')
        await main.run()

    if message.content.startswith('$stop'):
        bf.isSearching = False
        await message.channel.send('Shutting down search...')


    if message.content.startswith('$help'):
        await message.channel.send(
            'List of commands: '
            '\n\t$run_search to start searching for bourbon'
            '\n\t$blanton ...')

client.run(bot)