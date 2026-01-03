from typing import Any
from .widgets import grid

def render_to_string(renderable: Any) -> str:
    """
    Converts any renderable object (String, List, Widget) into a final string.
    """
    if isinstance(renderable, (list, tuple)):
        return grid(renderable, cols=1, render=True)

    text = str(renderable)
    if text.endswith('\n'):
        text = text.rstrip('\n')

    return text