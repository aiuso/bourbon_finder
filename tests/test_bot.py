import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import bot


class FakeMessage:
    def __init__(self, content, author="frank"):
        self.content = content
        self.author = author
        self.channel = MagicMock()
        self.channel.send = AsyncMock()


@pytest.fixture
def client():
    return bot.BourbonBot()


def sent(msg):
    return msg.channel.send.call_args.args[0]


def test_intents_allow_reading_messages(client):
    assert client.intents.message_content


def test_ignores_own_messages(client):
    msg = FakeMessage("$hello", author=None)
    with patch.object(type(client), "user", None):
        asyncio.run(client.on_message(msg))
    msg.channel.send.assert_not_called()


def test_hello_and_help(client):
    msg = FakeMessage("$hello")
    asyncio.run(client.on_message(msg))
    assert sent(msg) == "Hello!"
    msg = FakeMessage("$help")
    asyncio.run(client.on_message(msg))
    assert "$run [bourbon]" in sent(msg) and "$stop" in sent(msg)


def test_run_status_stop(client):
    async def fake_run(self, continuous=True):
        self.is_searching = True
        while self.is_searching:
            await asyncio.sleep(0.01)

    async def scenario():
        run = FakeMessage("$run Eagle Rare")
        await client.on_message(run)
        assert "Eagle Rare" in sent(run)
        await asyncio.sleep(0.02)
        assert client.is_running()

        again = FakeMessage("$run")
        await client.on_message(again)
        assert "Already searching" in sent(again)

        status = FakeMessage("$status")
        await client.on_message(status)
        assert sent(status) == "Searching for Eagle Rare."

        stop = FakeMessage("$stop")
        await client.on_message(stop)
        assert sent(stop) == "Shutting down search..."
        await asyncio.wait_for(client.task, 1)
        assert not client.is_running()

    with patch.object(bot.BourbonSearch, "run", fake_run):
        asyncio.run(scenario())


def test_stop_when_idle(client):
    msg = FakeMessage("$stop")
    asyncio.run(client.on_message(msg))
    assert sent(msg) == "No search is running."


def test_main_requires_token():
    with pytest.raises(SystemExit):
        bot.main()
