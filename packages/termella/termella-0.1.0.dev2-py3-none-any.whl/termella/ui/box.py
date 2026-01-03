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

        total_w = width if width else 80
        padding_total = self.padding * (len(self.children) - 1)
        available = total_w - padding_total
        final_widths = [0] * len(self.children)
        used_space = 0

        for i, child in enumerate(self.children):
            w = 0
            if isinstance(child.width_req, int):
                w = child.width_req
            elif child.width_percent:
                w = int(total_w * child.width_percent)

            if w > 0:
                final_widths[i] = w
                used_space += w

        remaining = max(0, available - used_space)
        auto_children = [i for i, c in enumerate(self.children) if final_widths[i] == 0]

        if auto_children:
            per_item =remaining // len(auto_children)
            extra = remaining % len(auto_children)

            for i in auto_children:
                final_widths[i] = per_item
                if extra > 0:
                    final_widths[i] += 1
                    extra -= 1

        rendered_blocks = []
        max_h = 0

        for i, child in enumerate(self.children):
            w = final_widths[i]
            if w <= 0:
                rendered_blocks.append([])
                continue

            lines = child.render(width=w)
            rendered_blocks.append(lines)
            max_h = max(max_h, len(lines))

        output_lines = [""] * max_h
        pad_str = " " * self.padding

        for r in range(max_h):
            row_parts = []
            for i, block in enumerate(rendered_blocks):
                if r < len(block):
                    content = block[r]
                else:
                    content = ""

                from ..core import visible_len
                v_len = visible_len(content)
                fill = final_widths[i] - v_len

                if fill > 0:
                    content += (" " * fill)

                row_parts.append(content)

            output_lines[r] = pad_str.join(row_parts)

        return output_lines