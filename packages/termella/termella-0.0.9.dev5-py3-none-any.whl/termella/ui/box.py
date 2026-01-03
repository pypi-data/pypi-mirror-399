from .core import Widget
from ..widgets.layouts import columns

class Container(Widget):
    """Base class for widgets that contain other widgets."""
    def __init__(self, *children, padding=0):
        super().__init__()
        self.children = list(children)
        self.padding = padding

    def add(self, widget):
        self.children.append(widget)
        return self
    
class VBox(Container):
    """
    Vertical Box. Stacks children on top of each other.
    """
    def render(self):
        lines = []
        pad_line = ""

        for i, child in enumerate(self.children):
            child_lines = child.render()
            lines.extend(child_lines)

            if self.padding > 0 and i < len(self.children) - 1:
                lines.extend([""] * self.padding)

        return lines
    
class HBox(Container):
    """
    Horizontal Box. Places children side-by-side.
    """
    def render(self):
        if not self.children: return []

        block_str = columns(*self.children, padding=self.padding, render=True)
        if not block_str: return []
        return block_str.split('\n')