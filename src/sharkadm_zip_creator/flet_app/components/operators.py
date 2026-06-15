import pathlib
import textwrap

import flet as ft
from sharkadm.operator import Operator

from sharkadm_zip_creator.flet_app import utils
from sharkadm_zip_creator.flet_app import event



@ft.control
class OperatorCard(ft.Card):
    allow_turn_off: bool = True
    operator: dict = None
    expand: bool = True

    def init(self):
        self.name = self.operator["name"]

        self.operator_widgets = {}

        name = self.operator['name']
        self._main_cb = ft.Checkbox(name, on_change=self._on_change_main)
        if not self.allow_turn_off:
            self._main_cb.disabled = True
        if self.operator.get('active', True):
            self._main_cb.value = True
        self.operator_widgets['active'] = self._main_cb

        self._children_col = ft.Column()
        for key, value in self.operator.items():
            if key in ['name', 'active']:
                continue
            if type(value) is bool:
                wid = ft.Checkbox(key)
                wid.value = value
            elif type(value) is int:
                wid = ft.TextField(label=key,
                                   value=value,
                                   input_filter=ft.NumbersOnlyInputFilter())
            else:
                wid = ft.Text(key)
            self.operator_widgets[key] = wid
            self._children_col.controls.append(wid)

        self.content = ft.Container(
            content=ft.Row(
                [
                    self._main_cb,
                    self._children_col
                ]
            ),
            width=400,
            padding=10,
            expand=True,
        )

    @property
    def has_options(self) -> bool:
        return bool(len(self._children_col.controls))

    def _on_change_main(self, e):
        self._children_col.disabled = True
        if self._main_cb.value:
            self._children_col.disabled = False
        self._children_col.update()

    def get_info(self) -> dict:
        info = dict(name=self.name)
        for key, wid in self.operator_widgets.items():
            value = wid.value
            if (hasattr(wid, "input_filter") and
                    wid.input_filter and
                    isinstance(wid.input_filter, ft.NumbersOnlyInputFilter)):
                value = int(value)
            info[key] = value
        return info



@ft.control
class PostOperatorCard(ft.Card):
    allow_turn_off: bool = True
    operator: dict = None
    expand: bool = True

    def init(self):
        self.expand = True
        self.name = self.operator['name']

        self.operator_widgets = {}

        name = self.operator['name']
        self._main_cb = ft.Button(name, on_click=self._on_click_main)

        self._children_col = ft.Column()
        for key, value in self.operator.items():
            if key in ['name', 'active']:
                continue
            if type(value) is bool:
                wid = ft.Checkbox(key)
                wid.value = value
            else:
                wid = ft.Text(key)
            self.operator_widgets[key] = wid
            self._children_col.controls.append(wid)

        self.content = ft.Container(
            content=ft.Row(
                [
                    self._main_cb,
                    self._children_col
                ]
            ),
            width=400,
            padding=10,
        )

    def _on_click_main(self, e):
        info = self.get_info()
        info['name'] = self.name
        event.post_event(event.Events.RUN_EXPORTER, info)

    def get_info(self) -> dict:
        info = dict(name=self.name)
        for key, wid in self.operator_widgets.items():
            info[key] = wid.value
        return info





















class _Operator(ft.Row):
    def __init__(self, main_app, operator: dict):
        super().__init__()
        self.main_app = main_app
        self.expand = True
        self.name = operator['name']

        self.operator_widgets = {}

        name = operator['name']
        cb = ft.Checkbox(name)
        if operator.get('active', True):
            cb.value = True
        self.operator_widgets['active'] = cb

        col = ft.Column()
        for key, value in operator.items():
            if key in ['name', 'active']:
                continue
            if type(value) is bool:
                wid = ft.Checkbox(key)
            else:
                wid = ft.Text(key)
            self.operator_widgets[key] = wid
            col.controls.append(wid)

        self.controls = [
            cb,
            col
        ]

    def get_info(self) -> dict:
        info = dict(name=self.name)
        for key, wid in self.operator_widgets.items():
            info[key] = wid.value
        return info
