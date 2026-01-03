from typing import List, Tuple, Optional
from ..core import visible_len

class Widget:
    """
    Base class for Object-Oriented UI Components.
    Unlike functional widgets (termella.widgets.*), these maintain state.
    """
    def __init__(self, width: Optional[int] = None, height: Optional[int] = None):
        self.width_req = width
        self.height_req = height
        self.is_focused: bool = False
        self.focusable: bool = False
        self._rect: Tuple[int, int, int, int] = (0, 0, 0, 0)

    def set_rect(self, x: int, y: int, w: int, h: int) -> None:
        self._rect = (x, y, w, h)

    def check_hit(self, mx: int, my: int) -> bool:
        x, y, w, h = self._rect
        return (x <= mx < x + w) and (y <= my < y + h)

    def render(self) -> str:
        """
        Must return a list of strings (lines).
        """
        return []
    
    def __str__(self) -> str:
        """
        Allows the widget to be passed directly to print(), panel(), or App.render().
        """
        return "\n".join(self.render())
    
    def on_focus(self) -> None:
        """Called when widget gains focus."""
        self.is_focused = True

    def on_blur(self) -> None:
        """Called when widget loses focus."""
        self.is_focused = False

    def on_key(self, key: str) -> bool:
        """Handle keypress if focused. Return True if handled."""
        return False
    
    def on_click_event(self) -> None:
        pass