import pathlib

import flet as ft

from sharkadm_zip_creator.flet_app.saves import user_saves


class FrameSource(ft.Row):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self._all_paths = set()

        self._source_path = ft.Text()
        self._latest_source_path = ft.Text(size=10)
        col = ft.Column(expand=True)
        # col.controls.append(ft.Divider(height=9, thickness=3))
        row = ft.Row([
            self._get_pick_files_button(),
            ft.Text('eller'),
            self._get_pick_directory_button(),
            ft.Text('eller'),
            self._get_latest_source_row()
        ],
        # alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        path_row = ft.Row([
            ft.Text('Datakälla:'),
            self._source_path
        ])

        col.controls.append(row)
        col.controls.append(path_row)
        self.controls.append(col)
        self._add_user_saves()

    def _get_latest_source_row(self) -> ft.Row:
        self._btn_load_latest_source = ft.ElevatedButton('Ladda senaste ->', on_click=self._on_load_latest_data_source)
        row = ft.Row(
            [
                self._btn_load_latest_source,
                self._latest_source_path,
            ]
        )
        return row

    def _get_pick_files_button(self) -> ft.Row:
        pick_source_file_dialog = ft.FilePicker(on_result=self._on_pick_file)

        self.main_app.page.overlay.append(pick_source_file_dialog)
        self._pick_files_button = ft.ElevatedButton(
                        "Välj en datakälla från FIL",
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: pick_source_file_dialog.pick_files(
                            allow_multiple=False,
                            allowed_extensions=['xlsx'],
                            dialog_title='Välj en datakälla från FIL'
                        ))

        row = ft.Row(
                [
                    self._pick_files_button,
                ]
            )
        return row

    def _get_pick_directory_button(self) -> ft.Row:

        pick_source_directory_dialog = ft.FilePicker(on_result=self._on_pick_directory)

        self.main_app.page.overlay.append(pick_source_directory_dialog)
        self._pick_config_directory_button = ft.ElevatedButton(
                        "Välj en datakälla från MAPP",
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: pick_source_directory_dialog.get_directory_path(
                            dialog_title='Välj en datakälla från MAPP',
                            # initial_directory=None
                        ))

        row = ft.Row(
                [
                    self._pick_config_directory_button,
                ]
            )
        return row

    def _on_pick_file(self, e: ft.FilePickerResultEvent) -> None:
        if not e.files:
            return
        self._set_source_path(e.files[0].path)

    def _on_pick_directory(self, e: ft.FilePickerResultEvent) -> None:
        if not e.path:
            return
        self._set_source_path(e.path)

    def _set_source_path(self, path: str, update_latest_source: bool = True) -> None:
        self._source_path.value = path
        self._source_path.update()
        self.main_app.update_source(path)
        if update_latest_source:
            self.set_latest_source_path()

    def _on_load_latest_data_source(self, e):
        if not self._latest_source_path.value:
            self.main_app.shiw_info('Det finns ingen tidigare datakälla')
            return
        self._set_source_path(self._latest_source_path.value, update_latest_source=False)

    def _check_latest_data_source(self):
        self._btn_load_latest_source.disabled = True
        if self._latest_source_path.value:
            self._btn_load_latest_source.disabled = False
        self._btn_load_latest_source.update()
        if self._latest_source_path.value and not pathlib.Path(self._latest_source_path.value).exists():
            self._latest_source_path.value = ''

    @property
    def source_path(self) -> pathlib.Path | None:
        if not self._source_path.value:
            return None
        return pathlib.Path(self._source_path.value)

    def set_latest_source_path(self):
        self._check_latest_data_source()

        path = self._source_path.value
        if not path:
            return
        self._set_latest_source_path(path)
        self.export_user_saves()
        self._check_latest_data_source()
        # utils.custom_save.add('latest_data_source', path)

    # def load_latest_source_path(self):
    #     path = utils.custom_save.get('latest_data_source')
    #     if not path:
    #         return
    #     self._set_latest_source_path(path)

    def _set_latest_source_path(self, path: str):
        self._latest_source_path.value = path
        self._latest_source_path.update()

    def _add_user_saves(self):
        user_saves.add_settings(_latest_source_path=self._latest_source_path.value)

    def import_user_saves(self):
        user_saves.import_saves()
        self._latest_source_path.value = user_saves.get('_latest_source_path', '')
        self._latest_source_path.update()

    def export_user_saves(self):
        user_saves.export_saves()




