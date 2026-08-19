from collections.abc import Callable
from pathlib import Path

import flet as ft
from flet_app.language import get_text

from sharkadm_zip_creator.flet_app import event, widgets
from sharkadm_zip_creator.flet_app.app_source import SourceType
from sharkadm_zip_creator.flet_app.saves import UserSavesKeys, user_saves


@ft.control
class SourceTypeComponent(ft.Row):
    on_change: Callable = None
    source_type: str = None

    def init(self):
        self.radio_buttons = ft.RadioGroup(
            on_change=self._handle_selection_change,
            content=ft.Row(
                controls=[
                    ft.Radio(value=str(s).upper(), label=str(s).upper())
                    for s in SourceType
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            value=str(self.source_type).upper(),
        )
        # print(f"1: {self.radio_buttons.value=}")
        # self.radio_buttons.value = str(self.source_type).upper()
        # print(f"2: {self.radio_buttons.value=}")
        self.controls = [self.radio_buttons]

    def _handle_selection_change(self, e: ft.Event[ft.RadioGroup]):
        self.source_type = str(e.control.value).lower()
        if self.on_change:
            self.on_change(dict(value=str(e.control.value).lower()))


@ft.control
class SingleDataSourceComponent(ft.Row):
    def init(self):
        self._latest_source_path = ft.Text()
        self._latest_source_path.value = user_saves.get(
            UserSavesKeys.LATEST_SINGLE_DATA_SOURCE, ""
        )

        self._pick_file_button = widgets.SingleFilePickerButton(
            title=get_text("select_a_data_source_from_file"),
            # title="Välj en datakälla från FIL",
            on_pick=self._on_pick_new_source,
            initial_directory=self._latest_source_path.value,
            dialog_title=get_text("select_a_file"),
            allowed_extensions=["xlsx", "txt"],
        )
        self._pick_directory_button = widgets.DirectoryPickerButton(
            title=get_text("select_a_data_source_from_folder"),
            on_pick=self._on_pick_new_source,
            initial_directory=self._latest_source_path.value,
            dialog_title=get_text("select_a_folder"),
        )

        self.controls = [
            self._pick_file_button,
            ft.Text(get_text("or")),
            self._pick_directory_button,
            ft.Text(get_text("or")),
            ft.Row(
                [
                    ft.Button(
                        f"{get_text('load_latest')} ->",
                        on_click=self._on_load_latest_data_source,
                    ),
                    self._latest_source_path,
                ]
            ),
        ]

    @property
    def source_path(self) -> Path | None:
        if not self._latest_source_path.value:
            return None
        return Path(self._latest_source_path.value)

    def _on_pick_new_source(self, path: Path):
        self._set_source(path)

    def _set_source(self, path: Path | str):
        self._latest_source_path.value = str(path)
        self._latest_source_path.update()
        user_saves.set(UserSavesKeys.LATEST_SINGLE_DATA_SOURCE, path)
        event.post_event(
            event.Events.CHANGE_SINGLE_DATA_SOURCE,
            dict(path=Path(self._latest_source_path.value)),
        )

    def _on_load_latest_data_source(self, e: ft.Event[ft.Button]):
        # path = user_saves.get(UserSavesKeys.LATEST_SINGLE_DATA_SOURCE)
        path = self._latest_source_path.value
        if not path:
            return
        if not Path(path).exists():
            return
        self._set_source(path)
