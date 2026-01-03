from typing import List, Optional
from .core import Widget
from ..widgets.layouts import columns

class Container(Widget):
    """Base class for widgets that contain other widgets."""
    def __init__(self, *children: Widget, padding: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.children = list(children)
        self.padding = padding

    def add(self, widget: Widget):
        self.children.append(widget)
        return self
    
class VBox(Container):
    """
    Vertical Box. Stacks children on top of each other.
    """
    def render(self, width: Optional[int] = None) -> List[str]:
        lines = []
        for i, child in enumerate(self.children):
            child_w = width
            if child.width_req and isinstance(child.width_req, int):
                child_w = child.width_req
            elif child.width_percent and width:
                child_w = int(width * child.width_percent)

            child_lines = child.render(width=child_w)
            lines.extend(child_lines)

            if self.padding > 0 and i < len(self.children) - 1:
                lines.extend([""] * self.padding)

        return lines
    
class HBox(Container):
    """
    Horizontal Box. Places children side-by-side.
    """
    def render(self, width: Optional[int] = None) -> List[str]:
        if not self.children: return []

        final_widths = [0] * len(self.children)
        remaining_w = width if width else 80
        total_padding = self.padding * (len(self.children) - 1)
        remaining_w -= total_padding

        for i, child in enumerate(self.children):
            if isinstance(child.width_req, int):
                final_widths[i] = child.width_req
                remaining_w -= child.width_req

        if width:
            for i, child in enumerate(self.children):
                if child.width_percent:
                    w = int(width * child.width_percent)
                    final_widths[i] = w
                    remaining_w -= w

        auto_count = sum(1 for c in self.children if not c.width_req and not c.width_percent)
        if auto_count > 0 and remaining_w > 0:
            per_item = remaining_w // auto_count
            for i, child in enumerate(self.children):
                if final_widths[i] == 0:
                    final_widths[i] = per_item

        rendered_children = []
        for i, child in enumerate(self.children):
            lines = child.render(width=final_widths[i])
            block = "\n".join(lines)
            rendered_children.append(block)

        from ..widgets.layouts import columns
        block_str = columns(*rendered_children, padding=self.padding, render=True)

        if not block_str: return []
        return block_str.split('\n')