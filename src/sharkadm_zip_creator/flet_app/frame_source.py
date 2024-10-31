import pathlib

import flet as ft


class FrameSource(ft.Row):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self._all_paths = set()

        self._source_path = ft.Text()
        col = ft.Column(expand=True)
        # col.controls.append(ft.Divider(height=9, thickness=3))
        row = ft.Row([
            self._get_pick_files_button(),
            ft.Text('eller'),
            self._get_pick_directory_button()
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

    def _set_source_path(self, path: str = None) -> None:
        self._source_path.value = path
        self.main_app.update_source(path)

    @property
    def source_path(self) -> pathlib.Path | None:
        if not self._source_path.value:
            return None
        return pathlib.Path(self._source_path.value)




