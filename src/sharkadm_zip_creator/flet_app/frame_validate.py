import flet as ft
from sharkadm import workflow

from sharkadm_zip_creator.flet_app.frame_operations import FrameOperator


class FrameValidate(ft.Row):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self.frame_operators = FrameOperator(self.main_app)
        self.controls.append(self.frame_operators)

    def set_workflow(self, wflow: workflow.SHARKadmWorkflow, data_type: str) -> None:
        self.frame_operators.set_workflow(wflow, data_type)
