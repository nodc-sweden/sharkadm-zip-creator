import flet as ft
from sharkadm import workflow, sharkadm_exceptions

from sharkadm_zip_creator.flet_app.frame_workflow_export_options import FrameWorkflowExportOptions
from sharkadm_zip_creator.flet_app.frame_post_workflow_export_options import FramePostWorkflowExportOptions
from sharkadm_zip_creator.flet_app.frame_operations import FrameOperators
from sharkadm_zip_creator.flet_app import saves


class FrameValidate(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.expand = True
        self.main_app = main_app
        self._workflow: workflow.SHARKadmWorkflow | None = None

        self.frame_operators = FrameOperators(self.main_app)
        self.frame_options = FrameWorkflowExportOptions(self)
        self.frame_post_options = FramePostWorkflowExportOptions(self)

        option_row = ft.Row([
            self.frame_options,
            self.frame_post_options,
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        main_row = ft.Row([
            self.frame_operators,
            option_row
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.controls.append(main_row)

        # self.controls.append(ft.Row([
        #     self.frame_operators,
        #     self.frame_options,
        #     self.frame_post_options,
        # ], expand=True))

        self.controls.append(ft.ElevatedButton('Validera', on_click=self._on_validate))

    def _on_validate(self, e=None):
        if not self._workflow:
            self.main_app.show_info('Ingen fil vald!')
            return
        # if not self.main_app.zip_directory:
        #     self.main_app.show_info('Sökväg till zippaketen saknas!')
        #     return
        try:
            self.main_app.disable_frames()
            # self._update_workflow_with_options()
            self._workflow.start_workflow()
            self.main_app.enable_frames()
            saves.config_saves.export_saves()
            self.save_export_options()
        except:
            raise
        finally:
            self.main_app.enable_frames()
            self.main_app.reset_progress()
            self.main_app.show_info('Allt klart!')

    def set_workflow(self, wflow: workflow.SHARKadmWorkflow, data_type: str) -> None:
        self._workflow = wflow
        print(f'{wflow.exporters=}')
        self.frame_operators.set_workflow(wflow, data_type)

        self.load_export_options()
        self.frame_options.set_workflow(wflow, data_type, color='pink')
        self.frame_post_options.set_workflow(wflow, data_type, color='pink')

    # def _update_workflow_with_options(self):
    #     export_options = self.frame_options.workflow_export_options
    #     self._workflow.exporters = self._update_exports_with_zip_archive(export_options)
    #
    # def _update_exports_with_zip_archive(self, export_options: list[dict]) -> list[dict]:
    #     """Adds ZipPackage export to given export_options. Returns updated list"""
    #     new_list = []
    #     zip_archive_exporter_name = 'ZipArchive'
    #     export_found = False
    #     for item in export_options:
    #         if item['name'] == zip_archive_exporter_name:
    #             item['active'] = True
    #             export_found = True
    #         new_list.append(item)
    #     if not export_found:
    #         new_list.append(dict(
    #             name=zip_archive_exporter_name,
    #             active=True,
    #             export_directory=self.main_app.zip_directory
    #         ))
    #     return new_list

    def save_export_options(self):
        data = {'validation_exports': self.frame_options.workflow_export_options,
                'post_validation_exports': self.frame_post_options.workflow_export_options}
        saves.user_saves.add_settings(**data)
        saves.user_saves.export_saves()

    def load_export_options(self):
        options = saves.user_saves.get('validation_exports', [])
        self.frame_options.update_workflow_export_options(options)

        options = saves.user_saves.get('post_validation_exports', [])
        self.frame_post_options.update_workflow_export_options(options)

    def run_exporter(self, **kwargs) -> None:
        if not self._workflow:
            return
        try:
            self._workflow.export(**kwargs)
        except sharkadm_exceptions.DataHolderError:
            self.main_app.show_info('Detta kan endast göras efter du validerat')
        finally:
            self.save_export_options()

