import flet as ft
from sharkadm import workflow

from sharkadm_zip_creator.flet_app.frame_operations import FrameOperators


class FrameCreateZip(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self._workflow: workflow.SHARKadmWorkflow | None = None

        self.frame_operators = FrameOperators(self.main_app)
        self.controls.append(self.frame_operators)
        self.controls.append(ft.ElevatedButton('Skapa zip-paket', on_click=self._create_zip_archive))

    def _create_zip_archive(self, e=None):
        if not self._workflow:
            self.main_app.show_info('Ingen fil vald!')
            return
        self._workflow.start_workflow()

    def set_workflow(self, wflow: workflow.SHARKadmWorkflow, data_type: str) -> None:
        self._workflow = wflow
        self.frame_operators.set_workflow(wflow, data_type)

