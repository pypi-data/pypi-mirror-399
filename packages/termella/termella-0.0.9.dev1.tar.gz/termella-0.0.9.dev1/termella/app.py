import os
import sys
import time
from .ansi import (
    ALT_SCREEN_ENTER, ALT_SCREEN_EXIT,
    CURSOR_HIDE, CURSOR_SHOW,
    CLEAR_SCREEN, CLEAR_EOS, CURSOR_HOME,
    MOUSE_ON, MOUSE_OFF
)
from .widgets import grid
from .input.listener import InputListener

CURSOR_HOME = "\033[H"

class App:
    """
    Base class for Full-Screen TUI Applications.
    Handles the Event Loop and Screen Buffer management.
    """
    def __init__(self, refresh_rate=0.1, mouse=False):
        self._running = False
        self.refresh_rate = refresh_rate
        self.mouse_enabled = mouse
        self.listener = InputListener()
        self._last_update = 0
        self.width = 80
        self.height = 24

    def on_start(self):
        """Override this to run logic before the loop starts."""
        pass

    def on_stop(self):
        """Override this to run logic after the app exits."""
        pass

    def on_update(self):
        """Override this to define the main loop logic."""
        pass

    def on_key(self, key):
        """
        Override this to handle keypresses.
        key: 'a', 'ENTER', 'UP', 'ESC', etc.
        """
        if key == 'q' or key == 'ESC': self.exit()

    def on_click(self, x, y, btn): pass

    def on_resize(self, width, height):
        """Called when terminal dimensions change."""
        pass

    def render(self):
        """
        Return the UI to display.
        Should return a String, Widget, or List of Widgets.
        """
        return ""

    def exit(self):
        """Stops the application loop."""
        self._running = False

    def _check_resize(self):
        try:
            size = os.get_terminal_size()
            if size.columns != self.width or size.lines != self.height:
                self.width = size.columns
                self.height = size.lines
                self.on_resize(self.width, self.height)
                sys.stdout.write(CLEAR_SCREEN)
        except OSError:
            pass

    def _draw_frame(self):
        self._check_resize()

        self.on_update()

        view = self.render()
        if isinstance(view, (list, tuple)):
            content = grid(view, cols=1, render=True)
        else:
            content = str(view)

        sys.stdout.write(CURSOR_HOME)
        sys.stdout.write(content)
        sys.stdout.write(CLEAR_EOS)
        sys.stdout.flush()

        self._last_update = time.time()

    def run(self):
        """
        Starts the application.
        1. Enters Alternate Screen Buffer.
        2. Hides Cursor.
        3. Runs the Event Loop.
        4. Restores Terminal state on exit.
        """
        try:
            self._check_resize()
            # --- SETUP ---
            sys.stdout.write(ALT_SCREEN_ENTER)
            sys.stdout.write(CURSOR_HIDE)
            if self.mouse_enabled:
                if os.name != 'nt': sys.stdout.write(MOUSE_ON)
                self.listener.enable_mouse()
            sys.stdout.flush()

            self._running = True
            self.on_start()
            self._draw_frame()

            # --- LOOP ---
            while self._running:
                now = time.time()
                wait_time = max(0, self.refresh_rate - (now - self._last_update))
                has_input = self.listener.wait_for_input(wait_time)

                if has_input:
                    while self.listener.key_available():
                        key_data = self.listener.read_key()
                        if key_data:
                            if key_data.startswith("CLICK_"):
                                parts = key_data.split()
                                self.on_click(int(parts[1]), int(parts[2]), parts[0])
                            else:
                                self.on_key(key_data)
                    self._draw_frame()
                elif wait_time <= 0:
                    self._draw_frame()

        except KeyboardInterrupt:
            pass
        finally:
            # --- CLEANUP ---
            self.on_stop()
            if self.mouse_enabled:
                if os.name != 'nt': sys.stdout.write(MOUSE_OFF)
                self.listener.disable_mouse()
            sys.stdout.write(ALT_SCREEN_EXIT)
            sys.stdout.write(CURSOR_SHOW)
            sys.stdout.flush()