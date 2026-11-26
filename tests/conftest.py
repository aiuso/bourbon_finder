import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ENV_VARS = ["SID", "TOKEN", "phone_to", "phone_from", "discord_webhook_url",
            "bot_token", "chrome_binary", "headless"]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    """Isolate every test from the real .env and log file."""
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    import config
    import send
    monkeypatch.setattr(config, "LOG_FILE", str(tmp_path / "stock_log.txt"))
    monkeypatch.setattr(send, "_sms_client", None)

