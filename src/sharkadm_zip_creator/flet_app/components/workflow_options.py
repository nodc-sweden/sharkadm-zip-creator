import flet as ft
from sharkadm import workflow

from sharkadm_zip_creator.flet_app import constants
from sharkadm_zip_creator.flet_app.components import operators


@ft.control
class WorkflowOptionsComponent(ft.Container):
    label: str = "Alternativ vid körning"
    color: str = constants.COLOR_EXPORT_OPTIONS_SECONDARY
    expand: bool = True

    def init(self):
        self._lv_color = ft.Colors.GREY_500

        self.lv = ft.ListView(
            spacing=10,
            padding=20,
            # width=150,
            auto_scroll=False,
            expand=True,
        )

        self.content = ft.Container(
            bgcolor=self._lv_color,
            content=self.lv,
            height=500,
            expand=True,
            border_radius=30,
        )

        self._workflow_widgets = []
        self._saved_options = []

    def reset(self) -> None:
        self.lv.controls.clear()
        self._workflow_widgets = []

    def _get_operators(self, incoming_operators: list) -> list[dict]:
        operators = []
        for oper in incoming_operators:
            print(f"{oper=}")
            for i, saved_oper in enumerate(self._saved_options[:]):
                if oper["name"] == saved_oper["name"]:
                    updated_oper = {}
                    for key, value in oper.items():
                        updated_oper[key] = saved_oper.get(key, value)
                    operators.append(updated_oper)
                    self._saved_options.pop(i)
                    break
            else:
                operators.append(oper)
        return operators

    def set_workflow(self, wflow: workflow.SHARKadmWorkflow) -> None:
        self.reset()

        operators_info = self._get_show_options_for_operators(wflow)

        wid_list = [ft.Text(self.label, color="black"), ft.Divider(height=9, thickness=3)]
        # for exp in wflow.exporters:
        for oper in self._get_operators(operators_info):
            print(f"{oper=}")
            wid = operators.OperatorCard(operator=oper, allow_turn_off=False)
            if not wid.has_options:
                continue
            wid_list.append(wid)
            wid_list.append(ft.Divider(height=9, thickness=3))
            self._workflow_widgets.append(wid)
        self.lv.controls = wid_list
        self.lv.update()

    @staticmethod
    def _get_show_options_for_operators(wflow: workflow.SHARKadmWorkflow) -> list:
        infos = []
        show_opers = wflow.get("gui", {}).get("show_options_for_operators", [])
        for oper in wflow.operators_info:
            if oper["name"] not in show_opers:
                continue
            infos.append(oper)
            print(f"jaha: {oper=}")
        return infos

    @property
    def workflow_options(self) -> list:
        options = []
        for wid in self._workflow_widgets:
            options.append(wid.get_info())
        return options

    def update_workflow_export_options(self, options):
        self._saved_options = options
