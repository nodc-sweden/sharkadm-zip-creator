import asyncio
from typing import Callable, Self

import flet as ft
import sharkadm.utils
from sharkadm.config.config import Config

from sharkadm_zip_creator.flet_app.app_state import States


@ft.control
class StateComponent(ft.Container):
    on_change: Callable = None
    border_radius: int = 20
    state: str = None

    def init(self):
        self._running_check_sync: bool = False
        self._running_auto_check_sync: bool = False

        self._sync_test_tooltip = ft.Tooltip(message="")

        self._config: Config | None = None
        self._test_color = "GREEN"
        self._prod_color = "RED"
        self._color_mapper = dict(
            TEST=self._test_color,
            PROD=self._prod_color,
        )

        self.bgcolor = self._color_mapper[self.state.upper()]
        self.padding = ft.Padding(left=10, right=15, bottom=5, top=5)

        self.radio_buttons = ft.RadioGroup(
            on_change=self._handle_selection_change,
            content=ft.Row(
                controls=[
                    ft.Radio(value=str(s).upper(), label=str(s).upper()) for s in States
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            value=str(self.state).upper(),
        )
        self._sync_test_button = ft.Button(
            "Synka test", on_click=self._on_sync_test, tooltip=self._sync_test_tooltip
        )
        self._auto_sync_test_switch = ft.Switch(
            label="Synka test automatiskt", on_change=self._on_auto_sync_test
        )
        self.content = ft.Row(
            [
                self.radio_buttons,
                self._sync_test_button,
                self._auto_sync_test_switch,
            ]
        )

    def did_mount(self):
        self._running_check_sync = True
        self.page.run_task(self._check_sync)

    def will_unmount(self):
        self._running_check_sync = False
        self._running_auto_check_sync = False

    async def _check_sync(self):
        while self._running_check_sync:
            # old_title = self.
            if not self._config.test_is_synced_with_prod:
                sharkadm.utils.clear_cache()
                lines = ["Osynkade filer:", *self._config.unsynced_files]
                self._sync_test_tooltip.message = "\n".join(lines)
                self._sync_test_button.content = "Synka test (test är inte uppdaterad)"
                try:
                    self._sync_test_button.update()
                except RuntimeError:
                    pass
            await asyncio.sleep(3)

    async def _check_auto_sync(self):
        while self._running_auto_check_sync:
            # old_title = self.
            if not self._config.test_is_synced_with_prod:
                try:
                    self._on_sync_test()
                except RuntimeError:
                    pass
                # self._config.sync_test_with_prod()
            await asyncio.sleep(3)

    def _on_sync_test(self, e: ft.Event[ft.Button] | None = None) -> None:
        self._config.sync_test_with_prod()
        sharkadm.utils.clear_cache()
        self._sync_test_tooltip.message = ""
        self._sync_test_button.content = "Synka test"
        self._sync_test_button.update()

    def _on_auto_sync_test(self, e: ft.Event[ft.Switch]) -> None:
        if self._auto_sync_test_switch.value:
            self._running_auto_check_sync = True
            self.page.run_task(self._check_auto_sync)
        else:
            self._running_auto_check_sync = False

    def _handle_selection_change(self, e: ft.Event[ft.RadioGroup]):
        self.state = str(e.control.value).lower()
        self.bgcolor = self._color_mapper[self.state.upper()]
        self.update()

        if self.on_change:
            self.on_change(dict(value=str(e.control.value).lower()))

    def is_isolated(self):
        return True

    def set_config(self, config: Config) -> Self:
        self._config = config
        return self


class Countdown(ft.Text):
    def __init__(self, seconds):
        super().__init__()
        self.seconds = seconds

    def did_mount(self):
        self.running = True
        self.page.run_task(self.update_timer)

    def will_unmount(self):
        self.running = False

    async def update_timer(self):
        while self.seconds and self.running:
            mins, secs = divmod(self.seconds, 60)
            self.value = "{:02d}:{:02d}".format(mins, secs)
            self.update()
            await asyncio.sleep(1)
            self.seconds -= 1
