import flet as ft
from sharkadm_zip_creator.flet_app import utils
from sharkadm import utils as sharkadm_utils
from sharkadm import transformers
from sharkadm import validators
from sharkadm import exporters


class FrameSystem(ft.Row):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self.lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self.expand = True

        col = ft.Column([
            ft.ElevatedButton(text='Skapa sammanfattningsfil av transformers', on_click=self._create_transformers_summary),
            ft.ElevatedButton(text='Skapa sammanfattningsfil av validators', on_click=self._create_validators_summary),
            ft.ElevatedButton(text='Skapa sammanfattningsfil av exporters', on_click=self._create_exporters_summary),
            self.lv
        ],  spacing=20,
            expand=True)

        self.controls.append(col)

    def _create_transformers_summary(self, *args):
        if not utils.USER_DIR.exists():
            return
        path = utils.USER_DIR / 'sharkadm_transformers_summary.txt'
        transformers.write_transformers_description_to_file(path)
        sharkadm_utils.open_file_with_default_program(path)

    def _create_validators_summary(self, *args):
        if not utils.USER_DIR.exists():
            return
        path = utils.USER_DIR / 'sharkadm_validators_summary.txt'
        validators.write_validators_description_to_file(path)
        sharkadm_utils.open_file_with_default_program(path)

    def _create_exporters_summary(self, *args):
        if not utils.USER_DIR.exists():
            return
        path = utils.USER_DIR / 'sharkadm_exporters_summary.txt'
        exporters.write_exporters_description_to_file(path)
        sharkadm_utils.open_file_with_default_program(path)
