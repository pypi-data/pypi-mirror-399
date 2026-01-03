from ..core import visible_len

class Widget:
    """
    Base class for Object-Oriented UI Components.
    Unlike functional widgets (termella.widgets.*), these maintain state.
    """
    def __init__(self, width=None, height=None):
        self.width_req = width
        self.height_req = height
        self.is_focused = False
        self.focusable = False
        self._rect = (0, 0, 0, 0)

    def set_rect(self, x, y, w, h):
        self._rect = (x, y, w, h)

    def check_hit(self, mx, my):
        x, y, w, h = self._rect
        return (x <= mx < x + w) and (y <= my < y + h)

    def render(self):
        """
        Must return a list of strings (lines).
        """
        return []
    
    def __str__(self):
        """
        Allows the widget to be passed directly to print(), panel(), or App.render().
        """
        return "\n".join(self.render())
    
    def on_focus(self):
        """Called when widget gains focus."""
        self.is_focused = True

    def on_blur(self):
        """Called when widget loses focus."""
        self.is_focused = False

    def on_key(self, key):
        """Handle keypress if focused. Return True if handled."""
        return False