import asyncio
import shlex
import traceback
from pathlib import Path

from textual import work
from textual.app import App
from textual.screen import ModalScreen

from tooi import __version__, messages
from tooi.api.accounts import verify_credentials
from tooi.api.streaming import InstanceStreamer

from tooi.asyncio import create_async_context, set_async_context
from tooi.cache import download_images_cached
from tooi.commands import TooiCommandsProvider
from tooi.credentials import activate_account, load_credentials
from tooi.data.instance import get_instance_info
from tooi.entities import Account
from tooi.screens.compose import ComposeScreen
from tooi.screens.loading import LoadingScreen
from tooi.screens.messagebox import MessageBox
from tooi.screens.source import SourceScreen
from tooi.settings import Options, get_stylesheet_path
from tooi.utils.from_dict import from_response
from tooi.widgets.dialog import ConfirmationDialog


class TooiApp(App[None]):
    TITLE = "tooi"
    SUB_TITLE = __version__
    SCREENS = {"loading": LoadingScreen}
    CSS_PATH = "app.css"
    COMMANDS = App.COMMANDS | {TooiCommandsProvider}

    BINDINGS = [
        ("q", "pop_or_quit", "Quit"),
    ]

    def __init__(self, options: Options):
        base_css = Path("./app.css")
        user_css = get_stylesheet_path()
        css_path = [base_css, user_css] if user_css.exists() else [base_css]
        super().__init__(css_path=css_path)  # type: ignore

        self.options = options
        set_async_context(create_async_context(self))

    @work
    async def on_mount(self):
        from tooi.screens.accounts_screen import AccountsScreen

        credentials = load_credentials()
        if not credentials.active_acct:
            if acct := await self.push_screen_wait(AccountsScreen()):
                await activate_account(acct)
            else:
                # TODO: or something else?
                self.exit()

        self.push_screen("loading")
        self.load_initial_data()

    @work
    async def load_initial_data(self):
        from tooi.screens.main import MainScreen

        # TODO run in paralel, handle errors
        self.instance = await get_instance_info()

        response = await verify_credentials()
        account = await from_response(Account, response)

        self.instance.streamer = InstanceStreamer(self.instance)
        self.tabs = MainScreen(self.instance, account)
        self.switch_screen(self.tabs)

    @work
    async def open_accounts_screen(self):
        from tooi.screens.accounts_screen import AccountsScreen

        if acct := await self.push_screen_wait(AccountsScreen()):
            self.switch_screen(LoadingScreen())
            await activate_account(acct)
            self.load_initial_data()

    async def confirm(
        self,
        title: str,
        *,
        text: str | None = None,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
    ) -> bool:
        dialog = ConfirmationDialog(
            modal_title=title,
            modal_text=text,
            confirm_label=confirm_label,
            cancel_label=cancel_label,
        )
        return await self.push_screen_wait(dialog)

    def show_error_modal(
        self,
        message: str | None = None,
        title: str = "Error",
        ex: Exception | None = None,
    ):
        """Open a modal screen with an error."""
        message = message.strip() if message else ""
        if ex:
            if message:
                message += "\n\n"
            for line in traceback.format_exception(ex):
                message += line
        self.push_screen(MessageBox(title, message, error=True))

    @work
    async def action_pop_or_quit(self):
        if len(self.screen_stack) > 2:
            self.pop_screen()
        else:
            if await self.confirm("Quit tooi?", confirm_label="Quit"):
                self.exit()

    def close_modals(self):
        while isinstance(self.screen, ModalScreen):
            self.pop_screen()

    @work
    async def on_show_account(self, message: messages.ShowAccount):
        from tooi.screens.account import AccountScreen

        self.close_modals()
        if to_post := await self.push_screen_wait(AccountScreen(message.account)):
            self.post_message(to_post)

    def on_show_source(self, message: messages.ShowSource):
        self.push_screen(SourceScreen(message.status))

    def on_show_status_menu(self, message: messages.ShowStatusMenu):
        from tooi.screens.status_context import StatusMenuScreen

        self.push_screen(StatusMenuScreen(message.status))

    def on_status_reply(self, message: messages.StatusReply):
        self.push_screen(ComposeScreen(self.instance, message.status))

    def on_show_images(self, message: messages.ShowImages):
        if message.media_attachments:
            image_viewer = self.options.image_viewer
            if image_viewer:
                urls = [m.url for m in message.media_attachments]
                self._show_images(image_viewer, urls)
            else:
                from tooi.widgets.gallery import GalleryScreen

                self.push_screen(GalleryScreen(message.media_attachments))

    @work
    async def _show_images(self, image_viewer: str, urls: list[str]):
        """
        Open a local image viewer to display the given images, which should be a list of URLs.
        This returns immediately and starts the work in a background thread.
        """
        paths = await download_images_cached(urls)
        args = [image_viewer] + [str(p) for p in paths]
        cmd = shlex.join(args)

        # Spawn the image viewer.
        process = await asyncio.create_subprocess_shell(cmd)
        # ... and wait for it to exit.
        await process.communicate()
