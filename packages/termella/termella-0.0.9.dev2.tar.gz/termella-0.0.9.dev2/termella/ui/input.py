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