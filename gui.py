"""Tkinter front end: type a bourbon, pick single or continuous search, press Search."""
import asyncio
import threading

import config
from main import BourbonSearch

BG, FIELD, TEXT, ACCENT = "#2b2b2b", "#3a3f3f", "#a9b7c6", "#cc7832"
SINGLE, CONTINUOUS = 0, 1


class SearchController:
    """Runs searches in a background thread so the window stays responsive."""

    def __init__(self):
        self.runner = None
        self.thread = None

    def is_running(self):
        return self.thread is not None and self.thread.is_alive()

    def start(self, bourbon, continuous):
        if self.is_running():
            return False
        self.runner = BourbonSearch(bourbon.strip() or None)
        self.thread = threading.Thread(
            target=asyncio.run, args=(self.runner.run(continuous=continuous),), daemon=True)
        self.thread.start()
        return True

    def stop(self):
        if self.runner:
            self.runner.stop()


def build_window(controller=None):
    from tkinter import IntVar, Button, Entry, Frame, Label, LabelFrame, Radiobutton, StringVar, Tk, W

    controller = controller or SearchController()
    window = Tk()
    window.title("Bourbon Finder")
    window.geometry("400x180")
    window.configure(bg=BG)

    frame = Frame(window, bg=BG, pady=10)
    frame.pack()

    textbox = LabelFrame(frame, text="What bourbon are you looking for?", bg=BG, fg=TEXT, pady=10)
    textbox.pack(side="left")
    user_input = Entry(textbox, width=15, bg=FIELD, fg=ACCENT)
    user_input.insert(0, config.DEFAULT_BOURBON)
    user_input.pack()

    radio_buttons = LabelFrame(frame, text="Search Type", bg=BG, fg=TEXT)
    radio_buttons.pack(side="right")
    search_value = IntVar(value=SINGLE)
    for label, value in (("Single Search", SINGLE), ("Continuous", CONTINUOUS)):
        Radiobutton(radio_buttons, text=label, value=value, variable=search_value,
                    bg=BG, fg=TEXT, activebackground=ACCENT, selectcolor=FIELD).pack(anchor=W)

    status = StringVar(value="Tip: partial names match more listings (Blant, not Blanton's).")
    Label(window, textvariable=status, bg=BG, fg=TEXT).pack(side="bottom")

    def on_search():
        continuous = search_value.get() == CONTINUOUS
        if controller.start(user_input.get(), continuous):
            status.set(f"Searching for {controller.runner.bourbon}...")
        else:
            status.set("A search is already running.")

    def on_stop():
        controller.stop()
        status.set("Stopping after the current check...")

    buttons = Frame(window, bg=BG)
    buttons.pack(side="bottom", pady=5)
    for text, command in (("Search", on_search), ("Stop", on_stop)):
        Button(buttons, text=text, command=command, bg=FIELD, fg=TEXT,
               activebackground=ACCENT).pack(side="left", padx=5)
    return window


if __name__ == "__main__":
    build_window().mainloop()
