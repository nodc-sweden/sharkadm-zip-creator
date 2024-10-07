import flet as ft
from sharkadm import workflow

from sharkadm_zip_creator.flet_app.frame_export_options import FrameExportOptions
from sharkadm_zip_creator.flet_app.frame_operations import FrameOperators


class FrameValidate(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self.frame_operators = FrameOperators(self.main_app)
        self.frame_options = FrameExportOptions(self.main_app)

        self.controls.append(self.frame_operators)
        self.controls.append(self.frame_options)
        self.controls.append(ft.ElevatedButton('Validera'))

    def set_workflow(self, wflow: workflow.SHARKadmWorkflow, data_type: str) -> None:
        self._workflow = wflow
        self.frame_operators.set_workflow(wflow, data_type)
