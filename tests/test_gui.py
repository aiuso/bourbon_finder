"""Tests the GUI's search controller. The Tk window itself is not opened."""
import time
from unittest.mock import patch

import gui


def test_controller_runs_single_search_with_user_input():
    controller = gui.SearchController()
    with patch.object(gui.BourbonSearch, "search_once") as once:
        assert controller.start("  Weller  ", continuous=False)
        controller.thread.join(2)
    assert controller.runner.bourbon == "Weller"
    once.assert_called_once()
    assert not controller.is_running()


def test_controller_blocks_second_search_and_stops():
    controller = gui.SearchController()
    with patch.object(gui.BourbonSearch, "search_once"), patch("main.send.discord_msg"):
        assert controller.start("Blant", continuous=True)
        time.sleep(0.05)
        assert controller.is_running()
        assert not controller.start("Other", continuous=True)
        controller.stop()
        controller.thread.join(3)
    assert not controller.is_running()


def test_empty_input_uses_default():
    controller = gui.SearchController()
    with patch.object(gui.BourbonSearch, "search_once"):
        controller.start("", continuous=False)
        controller.thread.join(2)
    assert controller.runner.bourbon == gui.config.DEFAULT_BOURBON
