from dataclasses import dataclass
from typing import Any

import flet as ft
from flet_app.components import SearchComponent
from sharkadm import utils as sharkadm_utils

from sharkadm_zip_creator.flet_app import utils
from sharkadm_zip_creator.flet_app.language import get_text


@dataclass
class oldFrameLog(ft.Row):
    main_app: Any = None
    lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
    expand = True

    def init(self):
        col = ft.Column(
            [
                ft.ElevatedButton(
                    get_text("open_log_directory"), on_click=self._open_log_directory
                ),
                self.lv,
            ],
            expand=True,
        )

        self.controls.append(col)

    def _open_log_directory(self, *args):
        if not utils.USER_DIR.exists():
            return
        sharkadm_utils.open_file_or_directory(utils.USER_DIR)

    def clear_text(self) -> None:
        self.lv.controls = []
        self.lv.update()

    def add_text(self, text: str) -> None:
        self.lv.controls.append(ft.Text(text))
        self.lv.update()

    def add_empty_line(self) -> None:
        self.add_text("\n")


@dataclass
class FrameLog(ft.Row):
    main_app: Any = None
    lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
    expand = True

    def init(self):
        self._logs: list[str] = []
        self._text = ft.Text()
        self._search_component = SearchComponent(on_change=self._on_search)

        self._container = ft.Container(
            width=1100,
            content=ft.Column(
                [
                    self._search_component,
                    # SCROLLBAR DEL
                    ft.Container(
                        # width=600,
                        expand=True,
                        border=ft.Border.all(1),
                        content=ft.ListView(
                            controls=[self._text],
                            expand=True,
                            spacing=10,
                            auto_scroll=False,
                        ),
                    ),
                    ft.Divider(),
                    ft.Button(
                        get_text("open_log_directory"), on_click=self._open_log_directory
                    ),
                ],
                expand=True,
            ),
        )

        self.controls.append(self._container)

    def _on_search(self, text: str):
        self._update_text(self._search_component.filter_list(self._logs))

    def _open_log_directory(self, *args):
        if not utils.USER_DIR.exists():
            return
        sharkadm_utils.open_file_or_directory(utils.USER_DIR)

    def clear_text(self) -> None:
        self._text.value = ""
        self._text.update()

    def _update_text(self, logs: list[str] | None = None) -> None:
        if logs is None:
            logs = self._logs
        self._text.value = "\n".join(logs)
        self._text.update()

    def add_text(self, text: str) -> None:
        self._logs.append(text)
        self._update_text()

    def add_empty_line(self) -> None:
        self.add_text("\n")
