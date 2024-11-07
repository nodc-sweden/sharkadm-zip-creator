import pathlib
import shutil

import flet as ft
from sharkadm import utils as sharkadm_utils

from sharkadm_zip_creator.flet_app.constants import COLOR_CONFIG_MAIN, COLOR_DATASETS_MAIN
from sharkadm_zip_creator.flet_app.saves import config_saves


class FrameConfig(ft.Row):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self._config_paths = set()

        self.controls.append(ft.Row([
            self._get_option_column(),
            self._get_paths_row(),
        ]))

        self._add_controls_to_save()

    def update_frame(self):
        config_saves.import_saves(self)

    @property
    def env(self):
        return self._env_dropdown.value

    @property
    def trigger_url(self) -> str:
        return self._trigger_url.value.strip()

    @property
    def status_url(self) -> str:
        return self._status_url.value.strip()

    @property
    def datasets_directory(self) -> str:
        if self._static_variable_paths_column.visible:
            print(f'{type(self._datasets_directory)=}')
            return self._datasets_directory.value.strip()
        return self._datasets_directory_dynamic.value.strip()

    @property
    def config_directory(self) -> str:
        if self._static_variable_paths_column.visible:
            return self._config_directory.value.strip()
        return self._config_directory_dynamic.value.strip()

    @property
    def zip_directory(self) -> str:
        if self._static_variable_paths_column.visible:
            return self._zip_directory.value.strip()
        return self._zip_directory_dynamic.value.strip()

    def _set_dropdown_options(self) -> None:
        """Only sets options that have present config files"""
        self._env_dropdown.options = [ft.dropdown.Option(value) for value in config_saves.present_envs]

    def _get_option_column(self) -> ft.Column:
        self._env_dropdown = ft.Dropdown(
            width=100,
            on_change=self._on_change_env
        )
        self._set_dropdown_options()

        if 'TEST' in config_saves.present_envs:
            self._env_dropdown.value = 'TEST'

        self._trigger_btn = ft.ElevatedButton(text='Trigga import', on_click=self.main_app.trigger_import, bgcolor='green')
        self._update_config_files_btn = ft.ElevatedButton(text='Uppdatera listor', on_click=self.main_app.update_lists)

        return ft.Column([
            self._update_config_files_btn,
            self._get_import_config_button(),
            self._env_dropdown,
            self._trigger_btn
        ])

    def _get_paths_row(self) -> ft.Row:

        label_col = ft.Column([
            ft.Text('URL som triggar importen:'),
            ft.Text('URL som kollar status på importen:'),
            ft.Text('Mapp för dataset:'),
            ft.Text('Mapp för zip-paket:'),
            ft.Text('Mapp för configfiler:'),
        ])

        btn_col = ft.Column([
            ft.Text(),
            ft.Text(),
            ft.ElevatedButton(text='Öppna mapp', on_click=self._open_datasets_directory),
            ft.ElevatedButton(text='Öppna mapp', on_click=self._open_zip_directory),
            ft.ElevatedButton(text='Öppna mapp', on_click=self._open_config_directory)
        ])

        self._trigger_url = ft.Text()
        self._status_url = ft.Text()

        self._datasets_directory = ft.Text()
        self._zip_directory = ft.Text()
        self._config_directory = ft.Text()

        self._static_variable_paths_column = ft.Column([
            self._datasets_directory,
            self._zip_directory,
            self._config_directory
        ])

        self._dynamic_variable_paths_column = ft.Column([
            self._get_dataset_directory_row(),
            self._get_zip_directory_row(),
            self._get_config_directory_row(),
        ], visible=False)

        var_col = ft.Column([
            self._static_variable_paths_column,
            self._dynamic_variable_paths_column
        ])

        val_col = ft.Column([
            self._trigger_url,
            self._status_url,
            var_col
        ])

        return ft.Row([
            label_col,
            val_col,
            btn_col
        ])

    def _get_dataset_directory_row(self) -> ft.Row:

        self._datasets_directory_dynamic = ft.Text()

        pick_datasets_directory_dialog = ft.FilePicker(on_result=self.on_select_dataset_directory)

        self.main_app.page.overlay.append(pick_datasets_directory_dialog)
        self._pick_datasets_directory_button = ft.ElevatedButton(
            "Välj mapp för dataset",
            icon=ft.icons.UPLOAD_FILE,
            on_click=lambda _: pick_datasets_directory_dialog.get_directory_path(
                dialog_title='Välj mapp för dataset',
                initial_directory=self._datasets_directory_dynamic.value
            ))

        row = ft.Row(
            [
                self._datasets_directory_dynamic,
                self._pick_datasets_directory_button,
            ]
        )
        return row

    def _get_zip_directory_row(self) -> ft.Row:

        self._zip_directory_dynamic = ft.Text()

        pick_zip_directory_dialog = ft.FilePicker(on_result=self.on_select_zip_directory)

        self.main_app.page.overlay.append(pick_zip_directory_dialog)
        self._pick_zip_directory_button = ft.ElevatedButton(
            'Välj mapp för "lokala" zip-paket',
            icon=ft.icons.UPLOAD_FILE,
            on_click=lambda _: pick_zip_directory_dialog.get_directory_path(
                dialog_title='Välj mapp för "lokala" zip-paket',
                initial_directory=self._zip_directory_dynamic.value
            ))

        row = ft.Row(
            [
                self._zip_directory_dynamic,
                self._pick_zip_directory_button,
            ]
        )
        return row

    def _get_config_directory_row(self) -> ft.Row:

        self._config_directory_dynamic = ft.Text()

        pick_config_directory_dialog = ft.FilePicker(on_result=self.on_select_config_directory)

        self.main_app.page.overlay.append(pick_config_directory_dialog)
        self._pick_config_directory_button = ft.ElevatedButton(
                        "Välj mapp för configfiler",
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: pick_config_directory_dialog.get_directory_path(
                            dialog_title='Välj mapp för configfiler',
                            initial_directory=self._config_directory_dynamic.value
                        ))

        row = ft.Row(
                [
                    self._config_directory_dynamic,
                    self._pick_config_directory_button,
                ]
            )
        return row

    def _get_import_config_button(self) -> ft.Row:
        pick_config_files_dialog = ft.FilePicker(on_result=self._on_pick_config_files)

        self.main_app.page.overlay.append(pick_config_files_dialog)
        self._pick_config_files_button = ft.TextButton(
                        "Importera configfil(er)",
                        # icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: pick_config_files_dialog.pick_files(
                            allow_multiple=True,
                            allowed_extensions=['yaml']
                        ))

        row = ft.Row(
                [
                    self._pick_config_files_button,
                ]
            )
        return row

    def _on_pick_config_files(self, e: ft.FilePickerResultEvent) -> None:
        if not e.files:
            return
        valid_paths = []
        invalid_paths = []
        valid_mapping = dict((path.stem.lower(), path) for path in config_saves.valid_save_paths)
        for file in e.files:
            source_path = pathlib.Path(file.path)
            if not valid_mapping.get(source_path.stem.lower()):
                invalid_paths.append(source_path)
                continue
            valid_paths.append(source_path)
            shutil.copy2(source_path, valid_mapping[source_path.stem.lower()])

        self._set_dropdown_options()
        self._on_change_env()
        valid_str = '\n'.join([str(p) for p in valid_paths])
        invalid_str = '\n'.join([str(p) for p in invalid_paths])
        if not valid_paths:
            msg = f'Inga valda filer är godkända configfiler: \n{invalid_str}'
        elif invalid_paths:
            msg = f'Godkända configfiler som kopierats:\n{valid_str}\n\nIcke godkända configfiler:\n{invalid_str}'
        else:
            msg = f'Följande configfiler har kopierats:\n{valid_str}'
        self.main_app.show_dialog(msg)

    def on_select_dataset_directory(self, e: ft.FilePickerResultEvent) -> None:
        if not e.path:
            return
        self._datasets_directory_dynamic.value = e.path
        self._datasets_directory_dynamic.update()

    def on_select_zip_directory(self, e: ft.FilePickerResultEvent) -> None:
        if not e.path:
            return
        self._zip_directory_dynamic.value = e.path
        self._zip_directory_dynamic.update()

    def on_select_config_directory(self, e: ft.FilePickerResultEvent) -> None:
        if not e.path:
            return
        self._config_directory_dynamic.value = e.path
        self._config_directory_dynamic.update()

    def _open_datasets_directory(self, event=None):
        if not self.datasets_directory:
            return
        sharkadm_utils.open_directory(self.datasets_directory)

    def _open_zip_directory(self, event=None):
        if not self.zip_directory:
            return
        sharkadm_utils.open_directory(self.zip_directory)

    def _open_config_directory(self, event=None):
        if not self.config_directory:
            return
        sharkadm_utils.open_directory(self.config_directory)

    def _on_change_env(self, event=None):
        value = self._env_dropdown.value
        if value == 'LOKALT':
            self._static_variable_paths_column.visible = False
            self._dynamic_variable_paths_column.visible = True
            self._trigger_btn.disabled = True
        else:
            self._static_variable_paths_column.visible = True
            self._dynamic_variable_paths_column.visible = False
            self._trigger_btn.disabled = False

        self._static_variable_paths_column.update()
        self._dynamic_variable_paths_column.update()
        self._trigger_btn.update()

        config_saves.set_env(value)
        config_saves.import_saves(self)
        self.check_paths()
        self.show_env_message()

    def show_env_message(self, ):
        self.main_app.show_info(f'=' * 100)
        self.main_app.show_info(f'Jobbar mot {self._env_dropdown.value}')

    def check_paths(self):
        for cont in [self._datasets_directory_dynamic, self._config_directory_dynamic]:
            value = cont.value.strip()
            if not value:
                continue
            if not pathlib.Path(value).exists():
                cont.value = ''
                cont.update()

    def _add_controls_to_save(self):

        config_saves.add_control('_trigger_url', self._trigger_url)
        config_saves.add_control('_status_url', self._status_url)

        config_saves.add_control('_datasets_directory', self._datasets_directory)
        config_saves.add_control('_zip_directory', self._zip_directory)
        config_saves.add_control('_config_directory', self._config_directory)

        config_saves.add_control('_datasets_directory_dynamic', self._datasets_directory_dynamic)
        config_saves.add_control('_zip_directory_dynamic', self._zip_directory_dynamic)
        config_saves.add_control('_config_directory_dynamic', self._config_directory_dynamic)
