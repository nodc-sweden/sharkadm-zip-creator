import flet as ft
from sharkadm_zip_creator.flet_app import utils
from sharkadm import utils as sharkadm_utils
from sharkadm_zip_creator.flet_app import constants


class FrameExportOptions(ft.Container):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        row = ft.Row([
            ft.Text('Detta är val för ')
            ])
        self.content = row
        self.bgcolor = constants.COLOR_DATASETS_MAIN

