from typing import List, Optional
from .core import Widget
from ..markup import parse

class Label(Widget):
    """
    A widget that displays a string of text. Supports Markup.
    """
    def __init__(self, text: str, style: Optional[str] = None, align: str = "left", **kwargs):
        super().__init__(**kwargs)
        self.raw_text = text
        self.style_str = style
        self.align = align

    def render(self, width: Optional[int] = None) -> List[str]:
        if self.style_str:
            content = f"[{self.style_str}]{self.raw_text}[/]"
        else:
            content = self.raw_text

        renderable = parse(content)
        line = str(renderable)

        if width is not None:
            from ..core import visible_len
            v_len = visible_len(line)
            pad = max(0, width - v_len)

            if self.align == "right":
                line = (" " * pad) + line
            elif self.align == "center":
                l_pad = pad // 2
                r_pad = pad - l_pad
                line = (" " * l_pad) + line + (" " * r_pad)
            else:
                line = line + (" " * pad)

        return [line]