from dataclasses import dataclass
from typing import Any

import flet as ft
from sharkadm import utils as sharkadm_utils

from sharkadm_zip_creator.flet_app import utils
from sharkadm_zip_creator.flet_app.language import get_text


@dataclass
class FrameLog(ft.Row):
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
