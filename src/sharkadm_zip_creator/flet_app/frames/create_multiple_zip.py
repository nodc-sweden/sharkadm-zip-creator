import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import flet as ft
from flet_app.language import get_text
from sharkadm import workflow
from sharkadm.data import get_polars_data_holder

from sharkadm_zip_creator.flet_app import constants, event, widgets
from sharkadm_zip_creator.flet_app.components import SearchComponent
from sharkadm_zip_creator.flet_app.saves import UserSavesKeys, user_saves


@dataclass
class FrameCreateMultipleZip(ft.Column):
    expand: bool = True
    main_app: Any = None

    def init(self):
        self._all_sources: dict[str, Path] = dict()
        self._filtered_sources: dict[str, Path] = dict()
        self._latest_root_directory = ft.Text()
        self._latest_root_directory.value = user_saves.get(
            UserSavesKeys.LATEST_MULTIPLE_DATA_SOURCE_ROOT, ""
        )

        self._search_component = SearchComponent(on_change=self._on_filter_change)

        self._nr_loaded = ft.Text()
        self._nr_filtered = ft.Text()
        self._nr_selected = ft.Text()

        row_nr_loaded = ft.Row(
            [ft.Text(f"{get_text('select_a_folder')}:"), self._nr_loaded]
        )
        row_nr_filtered = ft.Row(
            [ft.Text(f"{get_text('number_filtered')}:"), self._nr_filtered]
        )
        row_nr_selected = ft.Row(
            [ft.Text(f"{get_text('number_selected')}:"), self._nr_selected]
        )

        nr_row = ft.Row([row_nr_loaded, row_nr_filtered, row_nr_selected])

        self._pick_directory_button = widgets.DirectoryPickerButton(
            title=get_text("select_a_root_folder_for_data"),
            on_pick=self._on_pick_new_root,
            initial_directory=self._latest_root_directory.value,
            dialog_title=get_text("select_a_root_folder_for_data"),
        )

        self._lv_color = ft.Colors.GREY_500

        self.lv = ft.ListView(
            spacing=10,
            padding=20,
            # width=150,
            auto_scroll=False,
            expand=True,
        )

        self._select_all = ft.Checkbox(
            get_text("select_all"), on_change=self._on_select_all
        )

        self._button_create_zips = ft.Button(
            get_text("create_zip_packages_for_selected"), on_click=self._on_create_zips
        )

        self._container = ft.Container(
            bgcolor="green",
            content=self.lv,
            height=400,
            expand=True,
            border_radius=30,
        )
        self.controls = [
            ft.Row(
                [
                    self._pick_directory_button,
                    ft.Button(
                        f"{get_text('load_latest')} ->",
                        on_click=self._on_load_latest_data_source,
                    ),
                    self._latest_root_directory,
                ]
            ),
            self._search_component,
            # filter_row,
            nr_row,
            ft.Divider(height=2, thickness=1),
            self._container,
            ft.Divider(height=5, thickness=2),
            ft.Row(
                [
                    self._select_all,
                    self._button_create_zips,
                ]
            ),
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
        self._update_filtered_sources()

        self.lv.controls.clear()
        for name, path in self._filtered_sources.items():
            self.lv.controls.append(
                ft.Checkbox(name, value=True, on_change=self._on_change_checkbox)
            )
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
        user_saves.set(UserSavesKeys.LATEST_MULTIPLE_DATA_SOURCE_ROOT, str(path))

    def _update_all_sources(self):
        self._all_sources = dict()
        for path in Path(self._latest_root_directory.value).iterdir():
            self._all_sources[path.name] = path

    def _update_filtered_sources(self):
        if not self._search_component.text:
            self._filtered_sources = self._all_sources.copy()
            return
        self._filtered_sources = self._search_component.filter_dict_keys(
            self._all_sources
        )

    @property
    def nr_loaded(self) -> int:
        return len(self._all_sources)

    @property
    def nr_filtered(self) -> int:
        return len(self._filtered_sources)

    @property
    def nr_selected(self) -> int:
        return len(self._get_selected())

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

    def _disable(self):
        event.post_event(event.Events.DISABLE, dict())
        self._button_create_zips.disabled = True
        self._button_create_zips.update()

    def _enable(self):
        event.post_event(event.Events.ENABLE, dict())
        self._button_create_zips.disabled = False
        self._button_create_zips.update()

    def _run_workflows(self):
        def run():
            # results = None
            error = None

            workflows = dict()
            results = dict()

            try:
                for name, path in self._get_selected().items():
                    data_holder = get_polars_data_holder(path)
                    wflow = workflows.setdefault(
                        data_holder.data_type_internal,
                        workflow.get_dv_workflow_for_data_type(
                            data_holder.data_type_internal
                        ),
                    )
                    event.post_event(
                        event.Events.SHOW_INFO,
                        dict(msg=f"Source {name} loaded with workflow {wflow}"),
                    )
                    wflow.set_data_sources(path)
                    exp = dict(
                        name="PolarsZipArchive",
                        export_directory=str(
                            self.main_app.config_component.zip_target_directory
                        ),
                    )
                    wflow.update_exporters([exp])
                    results[name] = wflow.start_workflow()
            except Exception as e:
                error = e
                raise

            finally:
                self.page.run_task(self._on_workflows_done, results, error)

        if not self.main_app.config_component.zip_target_directory:
            event.post_event(
                event.Events.SHOW_DIALOG, dict(msg="No zip target directory selected!")
            )
            self._enable()
            return

        threading.Thread(target=run, daemon=True).start()

    async def _on_workflows_done(self, results, error):

        def check_results(results: dict[str, Any]):
            msg_list = list()
            for name, msg in results.items():
                if not msg:
                    continue
                msg_list.append(f"{name}: {msg}")
            return "\n".join(msg_list)

        if error:
            event.post_event(
                event.Events.SHOW_DIALOG,
                dict(title=f"{get_text('something_went_wrong')}!", msg=str(error)),
            )
            self._enable()
            return

        # event.post_event(event.Events.SHOW_INFO, str(results))
        self._enable()

        result_msg = check_results(results)
        data = dict()
        if error:
            data["title"] = get_text("something_went_wrong")
            data["msg"] = str(error)
        elif result_msg:
            data["title"] = get_text("something_maybe_went_wrong")
            data["msg"] = result_msg
        else:
            data["title"] = get_text("all_done")
            msg_list = [f"{get_text('zip_packages_created_for')}:"]
            msg_list.extend(sorted(results.keys()))
            data["msg"] = "\n".join(msg_list)
        event.post_event(event.Events.SHOW_DIALOG, data)
        event.post_event(event.Events.RESET_PROGRESS, dict())
        # saves.config_saves.export_saves()
        # self.save_export_options()

    def _on_create_zips(self, e: ft.Event[ft.Button]) -> None:
        if not self.nr_selected:
            event.post_event(
                event.Events.SHOW_DIALOG,
                dict(
                    title=get_text("no_sources_selected"),
                    msg=get_text("check_sources"),
                ),
            )
            return
        try:
            self._disable()
            self._run_workflows()
        except Exception as e:
            failed_msg = str(e)
            print(f"{failed_msg=}")

    def update_layout(self):
        self._container.height = int(
            self.page.window.height * constants.LIST_VIEW_HEIGHT_PERCENTAGE / 100
        )
        self._container.update()
