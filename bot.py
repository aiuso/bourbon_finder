"""Discord bot: start and stop searches from a Discord channel.

Commands:  $run [bourbon]  $stop  $status  $hello  $help
"""
import asyncio

import discord

import config
from main import BourbonSearch

HELP_TEXT = (
    "List of commands:"
    "\n\t$run [bourbon]  start searching (default: {default})"
    "\n\t$stop           stop the current search"
    "\n\t$status         show what is being searched"
    "\n\t$hello          say hello"
)


class BourbonBot(discord.Client):
    def __init__(self, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True  # also enable "Message Content Intent" in the dev portal
        super().__init__(intents=intents, **kwargs)
        self.runner = None
        self.task = None

    def is_running(self):
        return self.task is not None and not self.task.done()

    async def on_ready(self):
        print(f"We have logged in as {self.user}")

    async def on_message(self, message):
        if message.author == self.user:
            return
        content = message.content.strip()
        command, _, arg = content.partition(" ")

        if command == "$hello":
            await message.channel.send("Hello!")
        elif command == "$run":
            if self.is_running():
                await message.channel.send(f"Already searching for {self.runner.bourbon}. Use $stop first.")
                return
            self.runner = BourbonSearch(arg.strip() or None)
            await message.channel.send(f"Search for {self.runner.bourbon} has started...")
            self.task = asyncio.create_task(self.runner.run())
        elif command == "$stop":
            if self.is_running():
                self.runner.stop()
                await message.channel.send("Shutting down search...")
            else:
                await message.channel.send("No search is running.")
        elif command == "$status":
            if self.is_running():
                await message.channel.send(f"Searching for {self.runner.bourbon}.")
            else:
                await message.channel.send("No search is running.")
        elif command == "$help":
            await message.channel.send(HELP_TEXT.format(default=config.DEFAULT_BOURBON))


def main():
    token = config.env("bot_token")
    if not token:
        raise SystemExit("Set bot_token in your .env file to run the Discord bot.")
    BourbonBot().run(token)


if __name__ == "__main__":
    main()
