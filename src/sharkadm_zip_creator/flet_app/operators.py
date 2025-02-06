import pathlib
import textwrap

import flet as ft

from sharkadm_zip_creator.flet_app import utils


class Operator(ft.Card):
    def __init__(self, parent, operator: dict):
        super().__init__()
        self.parent_control = parent
        self.expand = True
        self.name = operator['name']

        self.operator = {}

        name = operator['name']
        self._main_cb = ft.Checkbox(name, on_change=self._on_change_main)
        if operator.get('active', True):
            self._main_cb.value = True
        self.operator['active'] = self._main_cb

        self._children_col = ft.Column()
        for key, value in operator.items():
            if key in ['name', 'active']:
                continue
            if type(value) is bool:
                wid = ft.Checkbox(key)
                wid.value = value
            else:
                wid = ft.Text(key)
            self.operator[key] = wid
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

    def _on_change_main(self, e):
        self._children_col.disabled = True
        if self._main_cb.value:
            self._children_col.disabled = False
        self._children_col.update()

    def get_info(self) -> dict:
        info = dict(name=self.name)
        for key, wid in self.operator.items():
            info[key] = wid.value
        return info


class PostOperator(ft.Card):
    def __init__(self, parent, operator: dict):
        super().__init__()
        self.parent_control = parent
        self.expand = True
        self.name = operator['name']

        self.operator = {}

        name = operator['name']
        self._main_cb = ft.ElevatedButton(name, on_click=self._on_click_main)

        self._children_col = ft.Column()
        for key, value in operator.items():
            if key in ['name', 'active']:
                continue
            if type(value) is bool:
                wid = ft.Checkbox(key)
                wid.value = value
            else:
                wid = ft.Text(key)
            self.operator[key] = wid
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
        self.parent_control.run_exporter(**info)

    def get_info(self) -> dict:
        info = dict(name=self.name)
        for key, wid in self.operator.items():
            info[key] = wid.value
        return info





















class _Operator(ft.Row):
    def __init__(self, main_app, operator: dict):
        super().__init__()
        self.main_app = main_app
        self.expand = True
        self.name = operator['name']

        self.operator = {}

        name = operator['name']
        cb = ft.Checkbox(name)
        if operator.get('active', True):
            cb.value = True
        self.operator['active'] = cb

        col = ft.Column()
        for key, value in operator.items():
            if key in ['name', 'active']:
                continue
            if type(value) is bool:
                wid = ft.Checkbox(key)
            else:
                wid = ft.Text(key)
            self.operator[key] = wid
            col.controls.append(wid)

        self.controls = [
            cb,
            col
        ]

    def get_info(self) -> dict:
        info = dict(name=self.name)
        for key, wid in self.operator.items():
            info[key] = wid.value
        return info
