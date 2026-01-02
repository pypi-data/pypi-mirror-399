from ..core import visible_len

class Widget:
    """
    Base class for Object-Oriented UI Components.
    Unlike functional widgets (termella.widgets.*), these maintain state.
    """
    def __init__(self, width=None, height=None):
        self.width_req = width
        self.height_req = height
        self._cache = None

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