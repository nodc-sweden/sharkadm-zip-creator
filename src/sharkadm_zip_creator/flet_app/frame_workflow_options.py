import flet as ft
from sharkadm_zip_creator.flet_app import utils
from sharkadm import utils as sharkadm_utils, workflow
from sharkadm_zip_creator.flet_app import constants
from sharkadm_zip_creator.flet_app import operators
import yaml


class FrameWorkflowOptions(ft.Row):

    def __init__(self,
                 parent,
                 label: str = "Alternativ vid körning",
                 color: str = "",
                 ):
        super().__init__()
        self.parent_control = parent
        self.expand = True
        self._workflow_widgets = []
        self._saved_options = []
        self._label = label
        self._color = color or constants.COLOR_EXPORT_OPTIONS_SECONDARY

    def reset(self) -> None:
        self.controls = []
        self._workflow_widgets = []

    def _get_operators(self, incoming_operators: list) -> list[dict]:
        operators = []
        for oper in incoming_operators:
            print(f"{oper=}")
            for i, saved_oper in enumerate(self._saved_options[:]):
                if oper['name'] == saved_oper['name']:
                    updated_oper = {}
                    for key, value in oper.items():
                        updated_oper[key] = saved_oper.get(key, value)
                    operators.append(updated_oper)
                    # operators.append(saved_oper)
                    self._saved_options.pop(i)
                    break
            else:
                operators.append(oper)
        return operators

    # def set_options(self, wflow: workflow.SHARKadmWorkflow, color: str = None) -> None:
    def set_options(self, operators_info: list) -> None:
        self.reset()
        self.lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=False)

        wid_list = [
            ft.Text(self._label),
            ft.Divider(height=9, thickness=3)
        ]
        # for exp in wflow.exporters:
        for oper in self._get_operators(operators_info):
            wid = operators.OperatorCard(self, oper, allow_turn_off=False)
            if not wid.has_options:
                continue
            wid_list.append(wid)
            wid_list.append(ft.Divider(height=9, thickness=3))
            self._workflow_widgets.append(wid)

        self.lv.controls = wid_list
        self.controls.append(ft.Container(
            # width=100,
            content=self.lv,
            bgcolor=self._color,
            border_radius=20,
            padding=10,
            expand=True
        ))

    @property
    def workflow_options(self) -> list:
        options = []
        for wid in self._workflow_widgets:
            options.append(wid.get_info())
        return options

    def update_workflow_export_options(self, options):
        self._saved_options = options

    def run_exporter(self, **kwargs) -> None:
        self.parent_control.run_exporter(**kwargs)
