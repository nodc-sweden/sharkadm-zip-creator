from dataclasses import dataclass
from typing import Any, Callable

import flet as ft

from sharkadm_zip_creator.flet_app.app_state import States
from sharkadm_zip_creator.flet_app import utils
from sharkadm_zip_creator.flet_app import event
from sharkadm_zip_creator.flet_app.saves import config_saves
from sharkadm_zip_creator.flet_app.saves import user_saves


@ft.control
class StateComponent(ft.Container):
    on_change: Callable = None
    border_radius: int = 20
    state: str = None


    def init(self):
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
                controls=[ft.Radio(value=str(s).upper(), label=str(s).upper()) for s in States],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            value=str(self.state).upper()
        )
        self.content = ft.Row([self.radio_buttons])
        # print(f"1: {self.radio_buttons.value=}")
        # self.radio_buttons.value = str(self.state).upper()
        # print(f"2: {self.radio_buttons.value=}")
        # self.controls = [self.radio_buttons]

    def _handle_selection_change(self, e: ft.Event[ft.RadioGroup]):
        self.state = str(e.control.value).lower()
        self.bgcolor = self._color_mapper[self.state.upper()]
        self.update()

        if self.on_change:
            self.on_change(dict(value=str(e.control.value).lower()))

    def is_isolated(self):
        return True