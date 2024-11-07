import flet as ft
from sharkadm_zip_creator.flet_app import utils
from sharkadm import utils as sharkadm_utils, workflow
from sharkadm_zip_creator.flet_app import constants
from sharkadm_zip_creator.flet_app import operators


class FrameExportOptions(ft.Row):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.expand = True
        self._workflow_export_widgets = []

    def reset(self) -> None:
        self.controls = []
        self._workflow_export_widgets = []

    def set_workflow(self, wflow: workflow.SHARKadmWorkflow, data_type: str) -> None:
        self.reset()
        self.lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)

        wid_list = [
            ft.Text('Exportalternativ under körning'),
            ft.Divider(height=9, thickness=3)
        ]
        for exp in wflow.exporters:
            wid = operators.Operator(self.main_app, exp)
            wid_list.append(wid)
            wid_list.append(ft.Divider(height=9, thickness=3))
            self._workflow_export_widgets.append(wid)

        self.lv.controls = wid_list
        self.controls.append(ft.Container(
            content=self.lv,
            bgcolor=constants.COLOR_EXPORT_OPTIONS_SECONDARY,
            border_radius=20,
            padding=10,
            expand=True
        ))

    @property
    def workflow_export_options(self) -> list:
        options = []
        for wid in self._workflow_export_widgets:
            options.append(wid.get_info())
        return options
