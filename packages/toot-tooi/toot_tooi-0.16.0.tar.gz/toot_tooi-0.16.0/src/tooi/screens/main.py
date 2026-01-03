from textual import getters, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, TabbedContent, TabPane

from tooi import messages, goto
from tooi.api import timeline
from tooi.api.timeline import Timeline
from tooi.app import TooiApp
from tooi.context import account_name
from tooi.data.instance import InstanceInfo
from tooi.entities import Account
from tooi.panes.conversations_pane import ConversationsPane
from tooi.panes.search_pane import SearchPane
from tooi.panes.timeline_pane import TimelinePane
from tooi.screens.compose import ComposeScreen
from tooi.screens.goto_screen import GotoScreen
from tooi.screens.instance import InstanceScreen
from tooi.widgets.header import Header
from tooi.widgets.status_bar import StatusBar


class MainScreen(Screen[None]):
    """
    The primary app screen, which contains tabs for content.
    """

    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    MainScreen {
        StatusBar {
            height: 2; /* prevent overlap with Footer */
        }
    }
    """

    BINDINGS = [
        Binding("c", "compose", "Compose"),
        Binding("g", "goto", "Goto"),
        Binding("i", "show_instance", "Show Instance"),
        Binding("ctrl+d,ctrl+w", "close_current_tab", "Close tab"),
        Binding("ctrl+pageup", "previous_tab", "Previous tab"),
        Binding("ctrl+pagedown", "next_tab", "Next tab"),
        Binding(".", "refresh_timeline", "Refresh"),
        Binding("/", "open_search_tab", "Search"),
        Binding("1", "select_tab(1)", "Select tab #1", show=False),
        Binding("2", "select_tab(2)", "Select tab #2", show=False),
        Binding("3", "select_tab(3)", "Select tab #3", show=False),
        Binding("4", "select_tab(4)", "Select tab #4", show=False),
        Binding("5", "select_tab(5)", "Select tab #5", show=False),
        Binding("6", "select_tab(6)", "Select tab #6", show=False),
        Binding("7", "select_tab(7)", "Select tab #7", show=False),
        Binding("8", "select_tab(8)", "Select tab #8", show=False),
        Binding("9", "select_tab(9)", "Select tab #9", show=False),
        Binding("0", "select_tab(10)", "Select tab #10", show=False),
    ]

    def __init__(self, instance: InstanceInfo, account: Account):
        super().__init__()
        self.instance = instance
        self.account = account

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Header("tooi")
            # Start with the home timeline
            with TabbedContent():
                yield TimelinePane(self.instance, timeline.HomeTimeline(self.instance))
            yield StatusBar()
            yield Footer()

    async def open_timeline_tab(self, timeline: Timeline, initial_focus: str | None = None):
        pane = TimelinePane(self.instance, timeline, initial_focus=initial_focus)
        await self.open_pane(pane)

    async def open_pane(self, pane: TabPane):
        tc = self.query_one(TabbedContent)
        with self.app.batch_update():
            await tc.add_pane(pane)
            if pane.id:
                tc.active = pane.id
                self.on_tab_pane_activated(pane)

    # This is triggered when a tab is clicked, but not when the tab is activated
    # programatically, see: https://github.com/Textualize/textual/issues/4150
    @on(TabbedContent.TabActivated)
    def on_tab_activated(self, message: TabbedContent.TabActivated):
        tc = self.query_one(TabbedContent)
        tab_pane = tc.get_pane(message.tab)
        self.on_tab_pane_activated(tab_pane)

    def on_tab_pane_activated(self, tab_pane: TabPane):
        if isinstance(tab_pane, TimelinePane):
            tab_pane.batch_show_update()

    @on(TimelinePane.EventUpdated)
    def on_event_updated(self, message: TimelinePane.EventUpdated):
        for tab in self.query(TimelinePane):
            tab.update_event(message.event)

    @on(TimelinePane.EventDeleted)
    def on_event_deleted(self, message: TimelinePane.EventDeleted):
        for tab in self.query(TimelinePane):
            tab.remove_event(message.event)

    def action_compose(self):
        self.app.push_screen(ComposeScreen(self.instance))

    @work
    async def action_goto(self):
        where = await self.app.push_screen_wait(GotoScreen())
        if where:
            self.handle_goto(where)

    @on(messages.GotoMessage)
    async def handle_goto_message(self, message: messages.GotoMessage):
        self.handle_goto(message.where)

    @work
    async def handle_goto(self, where: goto.Goto):
        match where:
            case goto.GotoHomeTimeline():
                await self.open_timeline_tab(timeline.HomeTimeline(self.instance))
            case goto.GotoPersonalTimeline():
                await self.open_timeline_tab(
                    timeline.AccountTimeline(
                        instance=self.instance,
                        title=account_name(self.account.acct),
                        account_id=self.account.id,
                    )
                )
            case goto.GotoLocalTimeline():
                await self.open_timeline_tab(timeline.LocalTimeline(self.instance))
            case goto.GotoFederatedTimeline():
                await self.open_timeline_tab(timeline.FederatedTimeline(self.instance))
            case goto.GotoHashtagTimeline():
                await self.open_timeline_tab(timeline.TagTimeline(self.instance, where.tag))
            case goto.GotoNotifications():
                await self.open_timeline_tab(timeline.NotificationTimeline(self.instance))
            case goto.GotoConversations():
                await self.open_pane(ConversationsPane())
            case goto.GotoContextTimeline():
                # TODO: composing a status: event id by hand is probably not ideal.
                await self.open_timeline_tab(
                    timeline=timeline.ContextTimeline(self.instance, where.status_id),
                    initial_focus=f"status-{where.status_id}",
                )
            case _:
                pass

    def on_status_edit(self, message: messages.StatusEdit):
        if message.status.account.acct == self.account.acct:
            screen = ComposeScreen(
                self.instance,
                edit=message.status,
                edit_source=message.status_source,
            )
            self.app.push_screen(screen)

    async def action_show_instance(self):
        self.app.push_screen(InstanceScreen(self.instance))

    def action_select_tab(self, tabnr: int):
        tc = self.query_one(TabbedContent)
        tabs = tc.query(TabPane)
        if tabnr <= len(tabs):
            with self.app.batch_update():
                tab = tabs[tabnr - 1]
                if tab.id is not None:
                    tc.active = tab.id
                    self.on_tab_pane_activated(tab)

    def action_previous_tab(self):
        self._change_active_index(-1)

    def action_next_tab(self):
        self._change_active_index(1)

    def _change_active_index(self, delta: int):
        tc = self.query_one(TabbedContent)
        panes = tc.query(TabPane).nodes
        if len(panes) < 2:
            return

        active_index = self._get_active_pane_index(tc, panes)
        if active_index is None:
            return

        index = (active_index + delta) % len(panes)
        pane = panes[index]
        if pane.id is None:
            return

        tc.active = pane.id
        self.on_tab_pane_activated(pane)

    def _get_active_pane_index(self, tc: TabbedContent, panes: list[TabPane]) -> int | None:
        for index, pane in enumerate(panes):
            if pane.id == tc.active:
                return index

    async def action_close_current_tab(self):
        tc = self.query_one(TabbedContent)
        # Don't close last tab
        if tc.tab_count > 1:
            with self.app.batch_update():
                await tc.remove_pane(tc.active)
                if tc.active:
                    tab = tc.get_pane(tc.active)
                    self.on_tab_pane_activated(tab)

    async def action_refresh_timeline(self):
        tc = self.query_one(TabbedContent)
        pane = tc.get_pane(tc.active)
        if isinstance(pane, TimelinePane):
            await pane.refresh_timeline()

    async def action_open_search_tab(self):
        tc = self.query_one(TabbedContent)
        pane = SearchPane("Search")
        await tc.add_pane(pane)
        assert pane.id is not None
        tc.active = pane.id
        self.on_tab_pane_activated(pane)
