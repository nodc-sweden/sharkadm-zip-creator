import re
from typing import Any, Callable

import flet as ft


@ft.control
class SearchComponent(ft.Row):
    on_change: Callable = None

    def init(self):
        self._filter_field = ft.TextField(
            label="Filtrera",
            icon=ft.Icons.SEARCH,
            multiline=False,
            on_change=self._on_change_search_field,
        )

        btn_clear_filter_field = ft.Button("Rensa", on_click=self._on_clear_filter_field)

        self._case_sensitive = ft.Switch(
            label="Case sensitive", on_change=self._on_change_search_field
        )
        self._regex = ft.Switch(
            label="Använd regex", on_change=self._on_change_search_field
        )
        self._quick_search_row = ft.Row()

        self._quick_search_cont = ft.Container(
            bgcolor=ft.Colors.DEEP_ORANGE_ACCENT,
            padding=ft.Padding(left=10, right=15, bottom=5, top=5),
            content=ft.Column(
                [
                    # self._quick_search_title,
                    self._quick_search_row,
                ]
            ),
            expand=True,
            border_radius=30,
        )
        self._quick_search_cont.visible = False

        self.controls = [
            self._filter_field,
            btn_clear_filter_field,
            self._case_sensitive,
            self._regex,
            self._quick_search_cont,
        ]

    @property
    def text(self) -> str:
        return self._filter_field.value.strip()

    def _on_clear_filter_field(self, e: ft.Event[ft.Button]) -> None:
        self._filter_field.value = ""
        self._filter_field.update()
        self._on_change_search_field()

    def _on_quick_search(self, e: ft.Event[ft.Button], text: str) -> None:
        self._filter_field.value = text
        self._filter_field.update()
        self._on_change_search_field()

    def _on_change_search_field(self, e: ft.Event[ft.TextField] | None = None) -> None:
        if self.on_change:
            self.on_change(self._filter_field.value.strip())

    def update_quick_search(self, search_list: list[str]) -> None:
        self._quick_search_row.controls.clear()
        self._quick_search_cont.visible = False
        if search_list:
            self._quick_search_cont.visible = True
        n = 2
        for items in [search_list[i : i + n] for i in range(0, len(search_list), n)]:
            col = ft.Column(
                [
                    ft.Button(
                        item, on_click=lambda e, x=item: self._on_quick_search(e, x)
                    )
                    for item in items
                ]
            )
            self._quick_search_row.controls.append(col)

    def filter_list(self, lst: list[str]) -> list[str]:
        text = self.text
        new_list = []
        for item in lst:
            if self._regex.value:
                if self._case_sensitive.value and re.search(text, item):
                    new_list.append(item)
                elif not self._case_sensitive.value and re.search(
                    text, item, re.IGNORECASE
                ):
                    new_list.append(item)
            elif self._case_sensitive.value:
                if text in item:
                    new_list.append(item)
            else:
                if text.upper() in item.upper():
                    new_list.append(item)
        return new_list

    def filter_dict_keys(self, data: dict[str, Any]) -> dict[str, Any]:
        text = self.text
        new_data = dict()
        for key, value in data.items():
            if self._regex.value:
                if self._case_sensitive.value and re.search(text, key):
                    new_data[key] = key
                elif not self._case_sensitive.value and re.search(
                    text, key, re.IGNORECASE
                ):
                    new_data[key] = key
            elif self._case_sensitive.value:
                if text in key:
                    new_data[key] = key
            else:
                if text.upper() in key.upper():
                    new_data[key] = key
        return new_data
