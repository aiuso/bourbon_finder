"""Desktop window: type a bourbon, pick single or continuous search, press Search.

The look comes from ttkbootstrap with two custom "bourbon" themes (dark and light).
"""
import asyncio
import threading

import config
from main import BourbonSearch

SINGLE, CONTINUOUS = 0, 1
FONT = "Segoe UI"  # Windows system font. Tk picks a close match on other systems.
TIP = "Tip: partial names match more listings (Blant, not Blanton's)."

# Warm, whiskey-barrel colors. Keys follow ttkbootstrap's ThemeDefinition.
DARK_THEME = {
    "primary": "#c8813a", "secondary": "#9a8a7b", "success": "#6a9f58",
    "info": "#5b8fa8", "warning": "#e0a43a", "danger": "#c0533f",
    "light": "#e9dfd3", "dark": "#2a2420", "bg": "#1f1a17", "fg": "#efe6da",
    "selectbg": "#8a5a2b", "selectfg": "#ffffff", "border": "#4a4039",
    "inputfg": "#f6efe6", "inputbg": "#2d2622", "active": "#3a312b",
}
LIGHT_THEME = {
    "primary": "#a8642a", "secondary": "#8c7b6b", "success": "#4f8a3e",
    "info": "#3f7891", "warning": "#c98a1e", "danger": "#b0432f",
    "light": "#f3ece3", "dark": "#3b2f27", "bg": "#faf6f0", "fg": "#3b2f27",
    "selectbg": "#a8642a", "selectfg": "#ffffff", "border": "#d8cbbb",
    "inputfg": "#3b2f27", "inputbg": "#ffffff", "active": "#efe5d8",
}
DARK, LIGHT = "bourbon-dark", "bourbon-light"


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


def _register_themes(style):
    from ttkbootstrap.style import ThemeDefinition

    style.register_theme(ThemeDefinition(DARK, DARK_THEME, "dark"))
    style.register_theme(ThemeDefinition(LIGHT, LIGHT_THEME, "light"))


def build_window(controller=None, dark=True):
    import ttkbootstrap as tb
    from ttkbootstrap.constants import BOTH, DISABLED, LEFT, NORMAL, RIGHT, W, X

    controller = controller or SearchController()
    window = tb.Window(title="Bourbon Finder", themename="darkly")
    _register_themes(window.style)
    window.style.theme_use(DARK if dark else LIGHT)
    window.geometry("480x360")
    window.minsize(440, 340)

    page = tb.Frame(window, padding=(24, 20))
    page.pack(fill=BOTH, expand=True)

    # Header
    header = tb.Frame(page)
    header.pack(fill=X)
    tb.Label(header, text="Bourbon Finder", font=(FONT, 20, "bold"),
             bootstyle="primary").pack(side=LEFT)
    dark_mode = tb.BooleanVar(value=dark)
    tb.Checkbutton(header, text="Dark mode", variable=dark_mode, bootstyle="round-toggle",
                   command=lambda: window.style.theme_use(DARK if dark_mode.get() else LIGHT)
                   ).pack(side=RIGHT)
    tb.Label(page, text="Checks Mecklenburg ABC stores and the NC warehouse.",
             font=(FONT, 10), bootstyle="secondary").pack(anchor=W, pady=(2, 16))

    # Bourbon name
    tb.Label(page, text="What bourbon are you looking for?", font=(FONT, 10, "bold")
             ).pack(anchor=W)
    user_input = tb.Entry(page, font=(FONT, 12))
    user_input.insert(0, config.DEFAULT_BOURBON)
    user_input.pack(fill=X, pady=(4, 14), ipady=3)

    # Search type, shown as a two-part toggle
    tb.Label(page, text="Search type", font=(FONT, 10, "bold")).pack(anchor=W)
    choices = tb.Frame(page)
    choices.pack(fill=X, pady=(4, 18))
    search_value = tb.IntVar(value=SINGLE)
    for label, value in (("Single search", SINGLE), ("Continuous", CONTINUOUS)):
        tb.Radiobutton(choices, text=label, value=value, variable=search_value,
                       bootstyle="primary-outline-toolbutton", width=14
                       ).pack(side=LEFT, fill=X, expand=True, padx=(0, 6) if value == SINGLE else 0)

    # Buttons
    buttons = tb.Frame(page)
    buttons.pack(fill=X)
    search_button = tb.Button(buttons, text="Search", bootstyle="primary", width=12)
    search_button.pack(side=LEFT, fill=X, expand=True, padx=(0, 6), ipady=4)
    stop_button = tb.Button(buttons, text="Stop", bootstyle="danger-outline", width=12,
                            state=DISABLED)
    stop_button.pack(side=LEFT, fill=X, expand=True, ipady=4)

    # Status bar
    status_bar = tb.Frame(window, padding=(24, 8), bootstyle="dark")
    status_bar.pack(side="bottom", fill=X)
    status = tb.StringVar(value=TIP)
    tb.Label(status_bar, textvariable=status, font=(FONT, 9), bootstyle="inverse-dark"
             ).pack(side=LEFT)
    busy = tb.Progressbar(status_bar, mode="indeterminate", length=80, bootstyle="warning")

    def show_running(running):
        search_button.configure(state=DISABLED if running else NORMAL)
        stop_button.configure(state=NORMAL if running else DISABLED)
        if running:
            busy.pack(side=RIGHT)
            busy.start(12)
        else:
            busy.stop()
            busy.pack_forget()

    def watch():
        """Check every half second whether the search has ended, and reset the window."""
        if controller.is_running():
            window.after(500, watch)
        else:
            show_running(False)
            status.set("Search finished. Results are in the console, Discord and SMS.")

    def on_search(_event=None):
        continuous = search_value.get() == CONTINUOUS
        if controller.start(user_input.get(), continuous):
            status.set(f"Searching for {controller.runner.bourbon}...")
            show_running(True)
            window.after(500, watch)
        else:
            status.set("A search is already running.")

    def on_stop():
        controller.stop()
        stop_button.configure(state=DISABLED)
        status.set("Stopping after the current check...")

    search_button.configure(command=on_search)
    stop_button.configure(command=on_stop)
    user_input.bind("<Return>", on_search)
    user_input.focus_set()
    return window


if __name__ == "__main__":
    build_window().mainloop()
