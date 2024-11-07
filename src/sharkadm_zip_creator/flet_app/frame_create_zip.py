import flet as ft
from sharkadm import workflow

from sharkadm_zip_creator.flet_app.frame_export_options import FrameExportOptions
from sharkadm_zip_creator.flet_app.frame_operations import FrameOperators
from sharkadm_zip_creator.flet_app import saves


class FrameCreateZip(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.expand = True
        self.main_app = main_app
        self._workflow: workflow.SHARKadmWorkflow | None = None

        self.frame_operators = FrameOperators(self.main_app)
        self.frame_options = FrameExportOptions(self.main_app)

        self.controls.append(ft.Row([
            self.frame_operators,
            self.frame_options
        ], expand=True))
        self.controls.append(ft.ElevatedButton('Skapa zip-paket', on_click=self._create_zip_archive))

    def _create_zip_archive(self, e=None):
        if not self._workflow:
            self.main_app.show_info('Ingen fil vald!')
            return
        self.main_app.disable_frames()
        self._update_workflow_with_options()
        self._workflow.start_workflow()
        self.main_app.enable_frames()
        saves.config_saves.export_saves()

    def set_workflow(self, wflow: workflow.SHARKadmWorkflow, data_type: str) -> None:
        self._workflow = wflow
        self.frame_operators.set_workflow(wflow, data_type)
        self.frame_options.set_workflow(wflow, data_type)

    def _update_workflow_with_options(self):
        export_options = self.frame_options.workflow_export_options
        self._workflow.exporters = self._update_exports_with_zip_archive(export_options)

    def _update_exports_with_zip_archive(self, export_options: list[dict]) -> list[dict]:
        """Adds ZipPackage export to given export_options. Returns updated list"""
        new_list = []
        zip_archive_exporter_name = 'ZipArchive'
        export_found = False
        for item in export_options:
            if item['name'] == zip_archive_exporter_name:
                item['active'] = True
                export_found = True
            new_list.append(item)
        if not export_found:
            new_list.append(dict(
                name=zip_archive_exporter_name,
                active=True,
                export_directory=self.main_app.zip_directory
            ))
        return new_list

