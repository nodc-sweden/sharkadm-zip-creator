import flet as ft
from sharkadm import workflow

from sharkadm_zip_creator.flet_app import constants
from sharkadm_zip_creator.flet_app.components import operators


@ft.control
class PostWorkflowExportOptionsComponent(ft.Container):
    label: str = "Exportalternativ efter körning"
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

        self._workflow_export_widgets = []
        self._saved_options = []

    def reset(self) -> None:
        self.lv.controls.clear()
        self._workflow_export_widgets = []

    def _get_exporters(self, incoming_exporters) -> list[dict]:
        exporters = []
        for exp in incoming_exporters:
            for i, saved_exp in enumerate(self._saved_options[:]):
                if exp["name"] == saved_exp["name"]:
                    updated_exp = {}
                    for key, value in exp.items():
                        updated_exp[key] = saved_exp.get(key, value)
                    exporters.append(updated_exp)
                    self._saved_options.pop(i)
                    break
            else:
                exporters.append(exp)
        return exporters

    def set_workflow(
        self, wflow: workflow.SHARKadmWorkflow, color: str | None = None
    ) -> None:
        self.reset()
        wid_list = [ft.Text(self.label, color="black"), ft.Divider(height=9, thickness=3)]
        # for exp in wflow.exporters:
        for exp in self._get_exporters(wflow.exporters_info):
            wid = operators.PostOperatorCard(operator=exp)
            wid_list.append(wid)
            wid_list.append(ft.Divider(height=9, thickness=3))
            self._workflow_export_widgets.append(wid)

        self.lv.controls = wid_list
        self.lv.update()

    @property
    def workflow_export_options(self) -> list:
        options = []
        for wid in self._workflow_export_widgets:
            options.append(wid.get_info())
        return options

    def update_workflow_export_options(self, options):
        self._saved_options = options
