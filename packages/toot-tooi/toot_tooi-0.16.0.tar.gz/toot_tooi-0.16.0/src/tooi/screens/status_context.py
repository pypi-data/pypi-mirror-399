from textual import on
from textual.widgets import Static
from typing import Generator, cast

from tooi.entities import Status
from tooi.goto import GotoHashtagTimeline
from tooi.messages import GotoMessage, ShowAccount
from tooi.screens.modal import ModalScreen, ModalTitle
from tooi.widgets.menu import Menu, MenuItem, TagMenuItem


class StatusMenuScreen(ModalScreen[None]):
    DEFAULT_CSS = """
    StatusMenuScreen ListView {
        height: auto;
    }
    """

    def __init__(self, status: Status):
        self.status = status
        super().__init__()

    def compose_modal(self):
        yield ModalTitle(f"Status #{self.status.id}")
        yield Menu(*self.top_items())

        if self.status.original.tags:
            yield Static("")
            yield Static("[b]Hashtags:[/b]")
            yield Menu(*self.tag_items())

    def top_items(self) -> Generator[MenuItem, None, None]:
        account = self.status.account
        yield MenuItem("show_account", f"@{account.acct}")

        if self.status.reblog:
            account = self.status.reblog.account
            yield MenuItem("show_original_account", f"@{account.acct}")

    def tag_items(self):
        for tag in self.status.original.tags:
            yield TagMenuItem("show_tag", tag)

    @on(Menu.ItemSelected)
    def on_item_selected(self, message: Menu.ItemSelected):
        message.stop()

        match message.item.code:
            case "show_account":
                self.post_message(ShowAccount(self.status.account))
            case "show_original_account":
                self.post_message(ShowAccount(self.status.original.account))
            case "show_tag":
                item = cast(TagMenuItem, message.item)
                self.post_message(GotoMessage(GotoHashtagTimeline(item.tag.name)))
                self.dismiss()
            case _:
                pass
