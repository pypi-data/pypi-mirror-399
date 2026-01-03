from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from tooi.data.events import Event, NotificationEvent, StatusEvent
from tooi.widgets.event_detail import EventDetailPlaceholder
from tooi.widgets import notification_detail as n
from tooi.widgets.status_detail import StatusDetail


class EventDetailContainer(Widget):
    event: reactive[Event | None] = reactive(None, recompose=True)

    DEFAULT_CSS = """
    EventDetailContainer {
        width: 2fr;
        height: 100%;
    }
    """

    def compose(self):
        if self.event:
            match self.event:
                case StatusEvent():
                    yield StatusDetail(self.event)

                case NotificationEvent():
                    match self.event.notification.type:
                        case "follow":
                            yield n.NewFollowerDetail(self.event)
                        case "mention":
                            yield n.MentionDetail(self.event)
                        case "favourite":
                            yield n.FavouriteDetail(self.event)
                        case "poll":
                            yield n.PollDetail(self.event)
                        case "reblog":
                            yield n.ReblogDetail(self.event)
                        case _:
                            yield n.UnknownEventDetail(self.event)
                case _:
                    yield Static("Not implemented")
        else:
            yield EventDetailPlaceholder()
