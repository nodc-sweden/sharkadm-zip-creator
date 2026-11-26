from dataclasses import dataclass
from typing import Any

import flet as ft

from sharkadm_zip_creator.flet_app import constants


@dataclass
class FeedbackInfo(ft.Container):
    color: str = constants.COLOR_EXPORT_OPTIONS_SECONDARY
    expand: bool = True
    main_app: Any = None

    def init(self):
        self._default_text_size = 12
        self._text = ft.TextField(
            label="",
            text_size=self._default_text_size,
            multiline=True,
            min_lines=5,
            max_lines=12,
            expand=True,
            read_only=True,
        )
        self._button_copy_text = ft.Button(
            self.main_app.language.get_text("copy_text"), on_click=self._copy_text
        )

        self.content = ft.Column(
            [
                self._text,
                self._button_copy_text,
            ]
        )

    def reset(self) -> None:
        self._text.label = ""
        self._text.value = ""
        self.update()

    def set_text(self, text: str, text_size: int | None = None, label: str = ""):
        self._text.value = text
        self._text.label = label
        self._text.text_size = text_size or self._default_text_size
        self.update()

    async def _copy_text(self, e):
        if not self._text.value.strip():
            return
        await ft.Clipboard().set(self._text.value)
        self.page.show_dialog(ft.SnackBar("Text copied to clipboard"))
