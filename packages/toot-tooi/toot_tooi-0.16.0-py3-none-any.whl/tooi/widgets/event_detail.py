from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Static

from tooi.data.events import Event

class EventDetail(VerticalScroll):
    DEFAULT_CSS = """
    EventDetail {
        padding: 0 1;
        background: $surface;

        &:focus {
            background-tint: $foreground 5%;
        }
    }
    """

    # Add j/k bindings for scrolling
    BINDINGS = [
        Binding("up,k", "scroll_up", "Scroll Up", show=False),
        Binding("down,j", "scroll_down", "Scroll Down", show=False),
    ]

    def __init__(self, event: Event | None = None):
        self.event = event
        super().__init__()

    def update_event(self, event: Event):
        self.event = event
        self.on_event_updated()

    def on_event_updated(self) -> None:
        """Children can override this to update after the event has changed"""


class EventDetailPlaceholder(Widget):
    DEFAULT_CSS = """
    EventDetailPlaceholder {
        height: 100%;
    }
    """

    def compose(self):
        yield Static("Nothing selected")
