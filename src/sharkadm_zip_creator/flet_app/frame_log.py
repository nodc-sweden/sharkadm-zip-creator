import flet as ft
from sharkadm_zip_creator.flet_app import utils
from sharkadm import utils as sharkadm_utils


class FrameLog(ft.Row):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self.lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self.expand = True
        col = ft.Column([
            ft.ElevatedButton(text='Öppna mappen med loggar', on_click=self._open_log_directory),
            self.lv
        ], expand=True)

        self.controls.append(col)

    def _open_log_directory(self, *args):
        if not utils.USER_DIR.exists():
            return
        sharkadm_utils.open_directory(utils.USER_DIR)

    def clear_text(self) -> None:
        self.lv.controls = []
        self.lv.update()

    def add_text(self, text: str) -> None:
        self.lv.controls.append(ft.Text(text))
        self.lv.update()

    def add_empty_line(self) -> None:
        self.add_text('\n')
