import flet as ft
from sharkadm_zip_creator.flet_app import utils
from sharkadm import utils as sharkadm_utils
from sharkadm_zip_creator.flet_app import constants


class FrameExportOptions(ft.Row):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self.controls = [
            self._get_workflow_container(),
            self._get_post_workflow_container(),
            ]
        # self.bgcolor = constants.COLOR_EXPORT_OPTIONS_PRIMARY
        self.expand = True

    @property
    def workflow_run_qc(self):
        return self._wf_cb_run_qc.value

    @property
    def workflow_open_html_map(self):
        return self._wf_cb_open_html_map.value

    def _get_workflow_container(self) -> ft.Container:
        self._wf_cb_run_qc = ft.Checkbox('Utför automatisk kvalitetskontroll', check_color=constants.COLOR_EXPORT_OPTIONS_CHECKED)
        self._wf_cb_open_html_map = ft.Checkbox('Visa html-karta', check_color=constants.COLOR_EXPORT_OPTIONS_CHECKED)

        col = ft.Column([
            ft.Text('Alternativ under körning'),
            self._wf_cb_run_qc,
            self._wf_cb_open_html_map
        ])

        return ft.Container(
            content=col,
            bgcolor=constants.COLOR_EXPORT_OPTIONS_SECONDARY,
            border_radius=20,
            padding=10
        )

    def _get_post_workflow_container(self) -> ft.Container:
        col = ft.Column([
            ft.Text('Alternativ efter körning'),
            ft.ElevatedButton('Öppna HTML-karta')
        ])

        return ft.Container(
            content=col,
            bgcolor=constants.COLOR_EXPORT_OPTIONS_SECONDARY,
            border_radius=20,
            padding=10
        )