from typing import Any

import flet as ft
from sharkadm import workflow

from sharkadm_zip_creator.flet_app import event
from flet_app.app_state import State
from flet_app.components.operators_list import ListOperatorsComponent


@ft.control
class FrameCreateMultipleZip(ft.Column):
    expand: bool = True

    def init(self):
        # self._workflow: workflow.SHARKadmWorkflow | None = None
        # self._workflow_config_path = ft.Text()
        # config_path_row = ft.Row([
        #     ft.Text('Konfigurationsfil:'),
        #     self._workflow_config_path
        # ])
        # self.frame_operators = ListOperatorsComponent()
        #
        # event.subscribe(event.Events.CHANGE_SINGLE_DATA_SOURCE, self._on_change_source)

        self.controls = [
            ft.Text("Create multi zip")
        ]

    def _on_change_source(self, data: dict):
        pass


    # def set_workflow(self, wflow: workflow.SHARKadmWorkflow, data_type: str) -> None:
    #     self._workflow = wflow
    #     self._workflow_config_path.value = str(self._workflow.path)
        # self.frame_operators.set_workflow(wflow, data_type)
        #
        # self.load_export_options()
        # self.frame_operators_options.set_options(self._get_show_options_for_operators())
        # # self.frame_options.set_workflow(wflow)
        # self.frame_post_options.set_workflow(wflow)