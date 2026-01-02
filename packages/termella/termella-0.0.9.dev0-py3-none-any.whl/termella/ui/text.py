from .core import Widget
from ..markup import parse
from ..core import Text

class Label(Widget):
    """
    A widget that displays a string of text. Supports Markup.
    """
    def __init__(self, text, style=None, align="left"):
        super().__init__()
        self.raw_text = text
        self.style_str = style
        self.align = align

    def render(self):
        if self.style_str:
            content = f"[{self.style_str}]{self.raw_text}[/]"
        else:
            content = self.raw_text

        renderable = parse(content)

        return str(renderable).split('\n')