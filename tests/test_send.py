from unittest.mock import patch

import config
import send


def test_local_stock_message_lists_every_store():
    msg = send.local_stock_message("Blant", [["3", "Store 12"], ["1", "Store 40"]])
    assert msg.startswith("Local Stock Available! Blant is in stock")
    assert "There are 3 of Blant at Store 12" in msg
    assert "There are 1 of Blant at Store 40" in msg


def test_warehouse_message():
    assert send.warehouse_stock_message("Blant", 5) == \
        "5 cases of Blant in Raleigh warehouses. Monitor local stock!"


def test_warehouse_message_lists_products():
    msg = send.warehouse_stock_message("Blant", 766, [
        {"code": "27090", "brand": "Blanton's Single Barrel", "listing": "Allocation",
         "cases": 766, "size": ".75L"}])
    assert msg.endswith("\n766 cases of Blanton's Single Barrel .75L (NC code 27090, Allocation)")


def test_write_to_file_appends_lines():
    send.write_to_file("one")
    send.write_to_file("two")
    with open(config.LOG_FILE, encoding="utf-8") as f:
        assert f.read() == "one\ntwo\n"


def test_text_message_skipped_without_twilio_config():
    with patch.object(send, "Client") as client:
        assert send.text_message("hi") is None
    client.assert_not_called()


def test_text_message_uses_twilio(monkeypatch):
    for k, v in {"SID": "AC1", "TOKEN": "t", "phone_to": "+1999", "phone_from": "+1888"}.items():
        monkeypatch.setenv(k, v)
    with patch.object(send, "Client") as client:
        send.text_message("hi")
    client.assert_called_once_with("AC1", "t")
    client.return_value.messages.create.assert_called_once_with(to="+1999", from_="+1888", body="hi")


def test_discord_skipped_without_webhook():
    with patch.object(send, "DiscordWebhook") as hook:
        assert send.discord_msg("hi") is None
    hook.assert_not_called()


def test_discord_plain_message(monkeypatch):
    monkeypatch.setenv("discord_webhook_url", "https://discord.test/hook")
    with patch.object(send, "DiscordWebhook") as hook:
        send.discord_msg("not in stock")
    hook.assert_called_once_with(url="https://discord.test/hook", content="not in stock")
    hook.return_value.add_embed.assert_not_called()
    hook.return_value.execute.assert_called_once()


def test_discord_in_stock_pings_here_with_embed(monkeypatch):
    monkeypatch.setenv("discord_webhook_url", "https://discord.test/hook")
    with patch.object(send, "DiscordWebhook") as hook, patch.object(send, "DiscordEmbed") as embed:
        send.discord_msg("in stock!", in_stock=True)
    assert hook.return_value.content == "@here"
    assert embed.call_args.kwargs["description"] == "in stock!"
    hook.return_value.add_embed.assert_called_once_with(embed.return_value)


def test_alert_sends_everywhere():
    with patch.object(send, "discord_msg") as d, patch.object(send, "text_message") as t, \
            patch.object(send, "write_to_file") as w:
        send.text_of_warehouse_stock("Blant", 4)
    msg = send.warehouse_stock_message("Blant", 4)
    d.assert_called_once_with(msg, in_stock=True)
    t.assert_called_once_with(msg)
    w.assert_called_once_with(msg)
