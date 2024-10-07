import flet as ft
from sharkadm_zip_creator.flet_app import utils
from sharkadm import utils as sharkadm_utils
from sharkadm_zip_creator.flet_app import constants


class FrameExportOptions(ft.Container):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        row = ft.Row([
            self._get_workflow_container(),
            self._get_post_workflow_container(),
            ])
        self.content = row
        self.bgcolor = constants.COLOR_EXPORT_OPTIONS_PRIMARY
        self.expand = True

    @property
    def workflow_run_qc(self):
        return self._wf_cb_run_qc.value

    @property
    def workflow_open_html_map(self):
        return self._wf_cb_open_html_map.value

    def _get_workflow_container(self) -> ft.Container:
        col = ft.Column([ft.Text('Alternativ')])
        self._wf_cb_run_qc = ft.Checkbox('Utför automatisk kvalitetskontroll', check_color=constants.COLOR_EXPORT_OPTIONS_CHECKED)
        self._wf_cb_open_html_map = ft.Checkbox('Visa html-karta', check_color=constants.COLOR_EXPORT_OPTIONS_CHECKED)

        col.controls = [
            self._wf_cb_run_qc,
            self._wf_cb_open_html_map
        ]

        return ft.Container(
            content=col,
            bgcolor=constants.COLOR_EXPORT_OPTIONS_SECONDARY
        )

    def _get_post_workflow_container(self) -> ft.Container:
        row = ft.Row([ft.Text('lkasjföda')])

        return ft.Container(
            content=row,
            bgcolor=constants.COLOR_EXPORT_OPTIONS_SECONDARY
        )