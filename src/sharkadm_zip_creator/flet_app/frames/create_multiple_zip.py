from pathlib import Path
from typing import Any

import flet as ft
from sharkadm import workflow

from flet_app import widgets
from flet_app.saves import UserSavesKeys, user_saves
from sharkadm_zip_creator.flet_app import event
from flet_app.app_state import State
from flet_app.components.operators_list import ListOperatorsComponent


@ft.control
class FrameCreateMultipleZip(ft.Column):
    expand: bool = True

    def init(self):
        self._all_sources: dict[str, Path] = dict()
        self._filtered_sources: dict[str, Path] = dict()
        self._latest_root_directory = ft.Text()
        self._latest_root_directory.value = user_saves.get(UserSavesKeys.LATEST_MULTIPLE_DATA_SOURCE_ROOT, "")

        self._filter_field = ft.TextField(
            label="Filtrera",
            multiline=False,
            on_change=self._on_filter_change,
        )

        self._case_sensitive = ft.Switch(label="Case sensitive", on_change=self._on_change_case_sensitive)

        filter_row = ft.Row([
            self._filter_field,
            self._case_sensitive
        ])

        self._nr_loaded = ft.Text()
        self._nr_filtered = ft.Text()
        self._nr_selected = ft.Text()

        row_nr_loaded = ft.Row([ft.Text("Antal i mapp:"), self._nr_loaded])
        row_nr_filtered = ft.Row([ft.Text("Antal filtrerade:"), self._nr_filtered])
        row_nr_selected = ft.Row([ft.Text("Antal valda:"), self._nr_selected])

        nr_row = ft.Row([
            row_nr_loaded,
            row_nr_filtered,
            row_nr_selected
        ])

        self._pick_directory_button = widgets.DirectoryPickerButton(
            title="Välj en rootmapp för data",
            on_pick=self._on_pick_new_root,
            dialog_title="Välj en rootmapp för data",
        )

        self._lv_color = ft.Colors.GREY_500

        self.lv = ft.ListView(
            spacing=10,
            padding=20,
            # width=150,
            auto_scroll=False,
            expand=True,
        )

        self._select_all = ft.Checkbox("Välj alla",
                                       on_change=self._on_select_all
                                    )

        self.controls = [
            ft.Row(
                [
                    ft.Button("Ladda senaste ->",
                              on_click=self._on_load_latest_data_source)
                    ,
                    self._latest_root_directory,
                ]
            ),
            self._pick_directory_button,
            filter_row,
            nr_row,
            ft.Container(
                # bgcolor=self._lv_color,
            content=self.lv,
            height=500,
            expand=True,
            border_radius=30,
            ),
            ft.Divider(height=5, thickness=2),
            self._select_all,
        ]

    def _on_pick_new_root(self, path: Path):
        self._set_source(path)

    def _on_load_latest_data_source(self, e: ft.Event[ft.Button]):
        path = self._latest_root_directory.value
        if not path:
            return
        if not Path(path).exists():
            return
        self._set_source(path)

    def _on_filter_change(self, e: ft.Event[ft.TextField] | None = None):
        self._update_filtered_sources(self._filter_field.value.strip())

        self.lv.controls.clear()
        for name, path in self._filtered_sources.items():
            self.lv.controls.append(ft.Checkbox(name,
                                                value=True,
                                                on_change=self._on_change_checkbox
                                                ))
        self.lv.update()
        self._update_nr_filtered()
        self._update_nr_selected()
        self._update_select_all()

    def _get_selected(self) -> dict[str, Path]:
        selected = dict()
        for cont in self.lv.controls:
            if not cont.value:
                continue
            selected[cont.label] = self._all_sources[cont.label]
        return selected

    def _on_change_case_sensitive(self, e: ft.Event[ft.Switch]):
        self._on_filter_change()

    def _on_change_checkbox(self, e: ft.Event[ft.Checkbox] | None = None):
        self._update_nr_selected()
        self._update_select_all()

    def _on_select_all(self, e: ft.Event[ft.Checkbox] | None = None):
        value = self._select_all.value
        for cont in self.lv.controls:
            cont.value = value
        self.lv.update()
        self._update_nr_selected()

    def _set_source(self, path: Path | str):
        self._latest_root_directory.value = str(path)
        self._latest_root_directory.update()
        self._update_all_sources()
        self._update_nr_loaded()
        self._on_filter_change()
        user_saves.set(UserSavesKeys.LATEST_MULTIPLE_DATA_SOURCE_ROOT, path)
        # event.post_event(event.Events.CHANGE_SINGLE_DATA_SOURCE, dict(path=Path(self._latest_root_directory.value)))

    def _update_all_sources(self):
        self._all_sources = dict()
        for path in Path(self._latest_root_directory.value).iterdir():
            self._all_sources[path.name] = path

    def _update_filtered_sources(self, text: str):
        if not text:
            self._filtered_sources = self._all_sources.copy()
            return
        self._filtered_sources = dict()
        for name, path in self._all_sources.items():
            if self._case_sensitive.value:
                if text in name:
                    self._filtered_sources[name] = path
            else:
                if text.upper() in name.upper():
                    self._filtered_sources[name] = path

    @property
    def nr_loaded(self) -> int:
        return int(len(self._all_sources))

    @property
    def nr_filtered(self) -> int:
        return int(len(self._filtered_sources))

    @property
    def nr_selected(self) -> int:
        return int(len(self._get_selected()))

    def _update_nr_loaded(self) -> None:
        self._nr_loaded.value = str(self.nr_loaded)
        self._nr_loaded.update()

    def _update_nr_filtered(self) -> None:
        self._nr_filtered.value = str(self.nr_filtered)
        self._nr_filtered.update()

    def _update_nr_selected(self) -> None:
        self._nr_selected.value = str(self.nr_selected)
        self._nr_selected.update()

    def _update_select_all(self) -> None:
        self._select_all.value = self.nr_filtered == self.nr_selected
        self._select_all.update()



