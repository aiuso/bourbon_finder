import asyncio
from unittest.mock import MagicMock, patch

import main


def test_bourbon_is_not_overwritten():
    # main.init used to reset the bourbon to 'Blant', ignoring the GUI/bot input.
    assert main.BourbonSearch("Eagle Rare").bourbon == "Eagle Rare"
    assert main.BourbonSearch().bourbon == main.config.DEFAULT_BOURBON


def test_single_run_searches_once():
    runner = main.BourbonSearch("Blant")
    with patch.object(main.search, "warehouse") as wh, patch.object(main.search, "liquor_stores") as ls, \
            patch.object(main.send, "discord_msg") as discord:
        asyncio.run(runner.run(continuous=False))
    wh.assert_called_once_with("Blant")
    ls.assert_called_once_with("Blant")
    discord.assert_not_called()
    assert not runner.is_searching


def test_continuous_run_stops_and_does_not_hammer_sites():
    runner = main.BourbonSearch("Blant")

    async def scenario():
        task = asyncio.create_task(runner.run(continuous=True, poll_seconds=0.01))
        await asyncio.sleep(0.1)  # many poll cycles
        assert runner.is_searching
        assert len(runner.scheduler.jobs) == 3
        runner.stop()
        await asyncio.wait_for(task, 2)

    with patch.object(main.search, "warehouse") as wh, patch.object(main.search, "liquor_stores") as ls, \
            patch.object(main.send, "discord_msg") as discord:
        asyncio.run(scenario())
    # The original searched both sites every second; now only once up front, then on schedule.
    assert wh.call_count == 1 and ls.call_count == 1
    discord.assert_called_once_with("Search has ended.")
    assert runner.scheduler.jobs == []


def test_search_errors_do_not_stop_run():
    runner = main.BourbonSearch("Blant")
    with patch.object(main.search, "warehouse", side_effect=RuntimeError("down")), \
            patch.object(main.search, "liquor_stores") as ls:
        asyncio.run(runner.run(continuous=False))
    ls.assert_called_once()


def test_cli_once():
    with patch.object(main.BourbonSearch, "run", new=MagicMock()) as run, \
            patch.object(main.asyncio, "run") as arun:
        main.main(["Weller", "--once"])
    run.assert_called_once_with(continuous=False)
    arun.assert_called_once()
