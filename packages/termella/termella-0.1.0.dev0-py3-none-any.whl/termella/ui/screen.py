from .box import VBox

class Screen(VBox):
    """
    The root container for an App.
    It automatically fills the terminal dimensions.
    """
    def __init__(self, *children):
        super().__init__(*children, padding=0)
        self.width = 80
        self.height = 24

    def resize(self, w, h):
        self.width = w
        self.height = h

    def render(self):
        return super().render()