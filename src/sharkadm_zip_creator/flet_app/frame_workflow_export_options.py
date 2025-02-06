import flet as ft
from sharkadm_zip_creator.flet_app import utils
from sharkadm import utils as sharkadm_utils, workflow
from sharkadm_zip_creator.flet_app import constants
from sharkadm_zip_creator.flet_app import operators
import yaml


class FrameWorkflowExportOptions(ft.Row):

    def __init__(self, parent):
        super().__init__()
        self.parent_control = parent
        self.expand = True
        self._workflow_export_widgets = []
        self._saved_options = []

    def reset(self) -> None:
        self.controls = []
        self._workflow_export_widgets = []

    def _get_exporters(self, incoming_exporters) -> list[dict]:
        exporters = []
        for exp in incoming_exporters:
            for i, saved_exp in enumerate(self._saved_options[:]):
                if exp['name'] == saved_exp['name']:
                    exporters.append(saved_exp)
                    self._saved_options.pop(i)
                    break
            else:
                exporters.append(exp)
        return exporters

    def set_workflow(self, wflow: workflow.SHARKadmWorkflow, data_type: str, color: str = None) -> None:
        self.reset()
        self.lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=False)

        wid_list = [
            ft.Text('Exportalternativ under körning'),
            ft.Divider(height=9, thickness=3)
        ]
        # for exp in wflow.exporters:
        for exp in self._get_exporters(wflow.exporters):
            wid = operators.Operator(self, exp)
            wid_list.append(wid)
            wid_list.append(ft.Divider(height=9, thickness=3))
            self._workflow_export_widgets.append(wid)

        color = color or constants.COLOR_EXPORT_OPTIONS_SECONDARY
        self.lv.controls = wid_list
        self.controls.append(ft.Container(
            # width=100,
            content=self.lv,
            bgcolor=color,
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

    def update_workflow_export_options(self, options):
        self._saved_options = options

    def run_exporter(self, **kwargs) -> None:
        self.parent_control.run_exporter(**kwargs)
