import os
import pathlib
import time

import flet as ft
import nodc_codes
import sharkadm
from sharkadm import event
from sharkadm import workflow
from sharkadm import utils as sharkadm_utils

from sharkadm_zip_creator.flet_app import utils
from sharkadm_zip_creator.flet_app.frame_source import FrameSource

USER_DIR = utils.USER_DIR
SAVES_PATH = utils.SAVES_PATH
from sharkadm_zip_creator.flet_app import constants

from sharkadm_zip_creator.flet_app.saves import creator_saves
from sharkadm_zip_creator.archive_remover import ArchiveRemover

from sharkadm_zip_creator.flet_app.frame_config import FrameConfig
from sharkadm_zip_creator.flet_app.frame_log import FrameLog
from sharkadm_zip_creator.flet_app.frame_create_zip import FrameCreateZip
from sharkadm_zip_creator.flet_app.frame_validate import FrameValidate

from sharkadm_zip_creator.trigger import Trigger

from sharkadm_zip_creator import exceptions


class ZipArchiveCreatorGUI:
    def __init__(self):

        self.page = None

        event.subscribe('log_workflow', self._on_log_workflow)

        self.app = ft.app(target=self.main)

        self._remove_log_file()

    @property
    def log_file_path(self) -> pathlib.Path:
        return USER_DIR / 'zip_creator_log.txt'

    def _remove_log_file(self):
        if self.log_file_path.exists():
            os.remove(self.log_file_path)

    def _add_to_log_file(self, text: str) -> None:
        with open(self.log_file_path, 'a', encoding='cp1252') as fid:
            fid.write(f'{text}\n')

    def main(self, page: ft.Page):
        self.page = page
        self.page.title = 'Zip archive creator'
        self.page.window_height = 900
        self.page.window_width = 1700
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self._build()
        self._add_controls_to_save()
        creator_saves.import_saves(self)
        self.frame_config.show_env_message()
        # self.frame_config.check_paths()

    def update_page(self):
        self.page.update()

    def _build(self):
        self._dialog_text = ft.Text()
        self._dlg = ft.AlertDialog(
            title=self._dialog_text
        )

        self.frame_config = FrameConfig(self)
        self.frame_create_zip = FrameCreateZip(self)
        self.frame_validate = FrameValidate(self)

        self.frame_log = FrameLog(self)
        self.frame_source = FrameSource(self)

        self._info_text = ft.Text(bgcolor='gray')

        self._tabs = ft.Tabs(
            selected_index=1,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Skapa ZIP-paket",
                    icon=ft.icons.FOLDER_ZIP,
                    content=self.frame_create_zip,
                ),
                ft.Tab(
                    text="Validera",
                    icon=ft.icons.CHECKLIST,
                    content=self.frame_validate,
                ),
                ft.Tab(
                    text="Log",
                    icon=ft.icons.EDIT_DOCUMENT,
                    content=self.frame_log,
                ),
            ],
            expand=1, expand_loose=True
        )

        self._tabs.selected_index = 0

        self.page.controls.append(self.frame_config)
        self.page.controls.append(ft.Divider(height=5, thickness=2, color=constants.COLOR_DATASETS_MAIN))
        self.page.controls.append(self.frame_source)
        self.page.controls.append(ft.Divider(height=5, thickness=2, color=constants.COLOR_DATASETS_MAIN))
        self.page.controls.append(self._tabs)
        self.page.controls.append(self._info_text)
        self.update_page()

    def update_lists(self) -> None:
        nodc_codes.update_config_files()

    def trigger_import(self, *args, on_remove=False):
        if not (self.frame_config.trigger_url and self.frame_config.status_url):
            self.show_dialog('Du måste fylla i fälten för URL!')
            return
        rem = ArchiveRemover(sharkdata_datasets_directory=self.frame_config.datasets_directory)
        packs = rem.get_packages_waiting_to_be_removed()
        if not packs and on_remove:
            self.show_dialog('Det finns ingen info om vad som ska tas bort!')
            return
        if packs:
            msg = f'Det finns en remove.txt fil i datasetmappen med {len(packs)} rader. Vill du fortfarande trigga APIet?'
            if on_remove:
                msg = f'Är du säker på att du vill ta bort {len(packs)} paket?'
            self._trigger_dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text('WARNING: remove.txt'),
                content=ft.Text(msg),
                actions=[
                    ft.TextButton('Ja', on_click=self._trigger_import),
                    ft.TextButton('Nej', on_click=lambda x: self.page.close(self._trigger_dlg)),
                    ft.TextButton('Öppna filen', on_click=lambda x: sharkadm_utils.open_file_with_default_program(rem.remove_file_path)),
                ]
            )
            self.page.open(self._trigger_dlg)
        else:
            self._trigger_import()

    def _trigger_import(self, event=None):
        t0 = time.time()
        max_time = 10
        if hasattr(self, '_trigger_dlg'):
            self.page.close(self._trigger_dlg)
        self.show_info(f'Triggar import...')
        trig = Trigger(trigger_url=self.frame_config.trigger_url, status_url=self.frame_config.status_url)
        # time.sleep(0.2)
        rem = ArchiveRemover(sharkdata_datasets_directory=self.frame_config.datasets_directory,
                             zip_directory=self.frame_config.zip_directory, )
        packs = rem.get_packages_waiting_to_be_removed()
        self._disable_on_trigger_import()
        while True:
            try:
                trig.trigger_import()
                while rem.remove_file_path.exists():
                    time.sleep(0.2)
                break
            except exceptions.ImportNotAvailable:
                self.show_info('Triggern är inte tillgänglig. Försöker igen...')
                time.sleep(0.2)
                if (time.time() - t0) > max_time:
                    self.show_info(f'Triggern är inte tillgänglig. Försökte i {max_time} sekunder men nu ger jag upp!')
                    self._enable_on_trigger_import()
                    return
        if packs:
            self.show_info(f'Tar bort gamla paket under: {self.frame_config.zip_directory}!')
            rem.remove_old_packs_in_zip_directory(packs)
        self._enable_on_trigger_import()
        self.show_info(f'Importen/borttagningen är klar!')

    # def _disable_on_trigger_import(self):
    #     self._tabs_info.disabled = True
    #     self._tabs_info.update()
    #     self._trigger_btn.disabled = True
    #     self._trigger_btn.update()
    #     if hasattr(self, '_trigger_dlg'):
    #         self._trigger_dlg.disabled = True
    #         self._trigger_dlg.update()
    #
    # def _enable_on_trigger_import(self):
    #     self._tabs_info.disabled = False
    #     self._tabs_info.update()
    #     self._trigger_btn.disabled = False
    #     self._trigger_btn.update()
    #     if hasattr(self, '_trigger_dlg'):
    #         self._trigger_dlg.disabled = False
    #         self._trigger_dlg.update()

    def show_dialog(self, text: str):
        self.show_info(text)
        self._dialog_text.value = text
        self._open_dlg()

    def _open_dlg(self, *args):
        self.page.dialog = self._dlg
        self._dlg.open = True
        self.update_page()

    def _on_log_workflow(self, data: dict) -> None:
        level = data.get('level')
        if level == 'debug':
            return
        if level in ['warning', 'error']:
            level = level.upper()
        text = f'{level}: {data.get("msg")}'
        self.show_info(text)

    def show_info(self, msg: str = '') -> None:
        self._add_to_log_file(msg)
        self.frame_log.add_text(msg)
        self._info_text.value = msg
        self._info_text.update()

    def update_source(self, path: str) -> None:
        data_holder = sharkadm.get_data_holder(path)
        self.show_info('Data holder loaded')

        # Create
        wflow = workflow.get_dv_workflow_for_data_type(data_holder.data_type)
        self.frame_create_zip.set_workflow(wflow, data_holder.data_type)
        self._add_source_to_workflow(wflow)
        self.show_info('Workflow for creation is set up')

        wflow.save_config(utils.USER_DIR / 'test_create_workflow.yaml')

        # Validate
        wflow = workflow.get_dv_validation_workflow_for_data_type(data_holder.data_type)
        self.frame_validate.set_workflow(wflow, data_holder.data_type)
        self._add_source_to_workflow(wflow)
        self.show_info('Workflow for validation is set up')

        wflow.save_config(utils.USER_DIR / 'test_validate_workflow.yaml')

    def _add_source_to_workflow(self, wflow: workflow.SHARKadmWorkflow):
        path = self.frame_source.source_path
        if not path:
            wflow.set_data_sources()
        else:
            wflow.set_data_sources(path)

    def _add_controls_to_save(self):
        pass

        # creator_saves.add_control('page_add_archive._option_update_zip_archives', self.page_add_archive._option_update_zip_archives)
        # creator_saves.add_control('page_add_archive._option_copy_zip_archives_to_sharkdata', self.page_add_archive._option_copy_zip_archives_to_sharkdata)
        # creator_saves.add_control('page_add_archive._option_trigger_dataset_import', self.page_add_archive._option_trigger_dataset_import)
        #
        # creator_saves.add_control('page_remove_archive._option_create_remove_file', self.page_remove_archive._option_create_remove_file)
        # creator_saves.add_control('page_remove_archive._option_trigger_remove_file', self.page_remove_archive._option_trigger_remove_file)
        #
        # creator_saves.add_control('page_config._option_copy_config_to_sharkdata', self.page_config._option_copy_config_to_sharkdata)
        # creator_saves.add_control('page_config._option_trigger_config_import', self.page_config._option_trigger_config_import)


