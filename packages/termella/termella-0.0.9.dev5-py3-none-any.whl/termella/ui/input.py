from .core import Widget
from ..markup import parse
from ..core import Text

class Button(Widget):
    def __init__(self, label, on_click=None):
        super().__init__()
        self.label = label
        self.on_click_callback = on_click
        self.focusable = True

    def on_key(self, key):
        if key == 'ENTER' or key == 'SPACE':
            if self.on_click_callback:
                self.on_click_callback()
            return True
        return False
    
    def render(self):
        if self.is_focused:
            content = f"[black bg_cyan] > {self.label} < [/]"
        else:
            content = f"[white bg_blue]   {self.label}   [/]"

        renderable = parse(content)
        return [str(renderable)]
    
    pass

class TextInput(Widget):
    """
    A single-line text input field
    """
    def __init__(self, value="", placeholder="", width=20, password=False):
        super().__init__()
        self.value = value
        self.placeholder = placeholder
        self.width_req = width
        self.password = password
        self.focusable = True
        self.cursor_pos = len(value)

    def on_key(self, key):
        if key == 'BACKSPACE':
            if self.value:
                self.value = self.value[:-1]
                self.cursor_pos -= 1
            return True
        elif key == 'SPACE':
            self.value += " "
            self.cursor_pos += 1
            return True
        elif len(key) == 1:
            self.value += key
            self.cursor_pos += 1
            return True
        return False
    
    def render(self):
        if not self.value and not self.is_focused:
            display_text = self.placeholder
            style_tag = "dim"
        else:
            display_text = self.value
            style_tag = "white"

        val_to_show = self.value
        if self.password and val_to_show:
            val_to_show = "*" * len(val_to_show)

        if not self.value and not self.is_focused:
            display_text = self.placeholder
            style_tag = "dim"
        else:
            display_text = val_to_show
            style_tag = "white"

        pad_len = max(0, self.width_req - len(display_text))
        padding = "_" * pad_len

        if self.is_focused:
            cursor = "[reverse] [/-]"
            content = f"[{style_tag}]{display_text}[/]{cursor}[dim]{padding[:-1]}[/]"
            final = f"[cyan] > [/]{content}"
        else:
            content = f"[{style_tag}]{display_text}[/][dim]{padding}[/]"
            final = f"[dim]   [/]{content}"

        return [str(parse(final))]