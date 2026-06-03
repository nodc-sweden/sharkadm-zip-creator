import flet as ft
from sharkadm import workflow, sharkadm_exceptions
from nodc_occurrence_id import event as occ_event

from sharkadm_zip_creator.flet_app.frame_workflow_export_options import FrameWorkflowExportOptions
from sharkadm_zip_creator.flet_app.frame_post_workflow_export_options import FramePostWorkflowExportOptions
from sharkadm_zip_creator.flet_app.frame_operations import FrameOperators
from sharkadm_zip_creator.flet_app import saves
from sharkadm_zip_creator.flet_app.frame_workflow_options import FrameWorkflowOptions


class FrameCreateZip(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.expand = True
        self.main_app = main_app
        self._workflow: workflow.SHARKadmWorkflow | None = None

        self._dialog_messages = []

        occ_event.subscribe(occ_event.Events.NR_VALID_ADDED, self._on_occurrence_valid_added)
        occ_event.subscribe(occ_event.Events.NR_VALID_NOT_ADDED, self._on_occurrence_valid_not_added)
        occ_event.subscribe(occ_event.Events.DATABASE_IS_UPDATED, self._on_db_updated)

        self._build()

    def _build(self):
        self._workflow_config_path = ft.Text()
        config_path_row = ft.Row([
            ft.Text('Configurationsfil:'),
            self._workflow_config_path
        ])

        self.frame_operators = FrameOperators(self.main_app)
        # self.frame_options = FrameWorkflowExportOptions(self)
        self.frame_operators_options = FrameWorkflowOptions(self)
        self.frame_post_options = FramePostWorkflowExportOptions(self)
        # self.frame_options.visible = False

        self._option_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Under körning",
                    icon=ft.icons.RUN_CIRCLE,
                    content=self.frame_operators_options,
                ),
                ft.Tab(
                    text="Efter körning",
                    icon=ft.icons.POST_ADD_ROUNDED,
                    content=self.frame_post_options,
                ),
            ],
            expand=1, expand_loose=True
        )

        option_row = ft.Row([
            self._option_tabs
            # self.frame_operators_options,
            # self.frame_options,
            # self.frame_post_options,
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        main_row = ft.Row([
            self.frame_operators,
            option_row
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.controls.append(config_path_row)
        self.controls.append(main_row)

        # self.controls.append(ft.Row([
        #     self.frame_operators,
        #     self.frame_options,
        #     self.frame_post_options,
        # ], expand=True))

        self.controls.append(ft.ElevatedButton('Skapa zip-paket', on_click=self._create_zip_archive, scale=1.5))

    def _create_zip_archive(self, e=None):
        self._dialog_messages = []
        failed_msg = False
        if not self._workflow:
            self.main_app.show_info('Ingen fil vald!')
            return
        if not self.main_app.zip_directory:
            self.main_app.show_info('Sökväg till zip-paketen saknas!')
            return
        try:
            self.main_app.disable_frames()
            # self._update_workflow_with_options()
            info = self._workflow.start_workflow()
            if info:
                failed_msg = str(info.exception)
            else:
                saves.config_saves.export_saves()
                self.save_export_options()
        except Exception as e:
            failed_msg = str(e)
            raise
        self.main_app.enable_frames()
        self.main_app.reset_progress()
        if failed_msg:
            self.main_app.show_dialog(failed_msg)
        else:
            if self._dialog_messages:
                msg = f"Allt klart!\n" + "\n".join(self._dialog_messages)
                self.main_app.show_dialog(msg)
            else:
                self.main_app.show_info("Allt klart!")

    def set_workflow(self, wflow: workflow.SHARKadmWorkflow, data_type: str) -> None:
        self._workflow = wflow
        self._workflow_config_path.value = str(self._workflow.path)
        print(f'{wflow.exporters=}')
        self.frame_operators.set_workflow(wflow, data_type)

        self.load_export_options()
        self.frame_operators_options.set_options(self._get_show_options_for_operators())
        # self.frame_options.set_workflow(wflow)
        self.frame_post_options.set_workflow(wflow)

    def _get_show_options_for_operators(self) -> list:
        infos = []
        show_opers = self._workflow.get("gui", {}).get("show_options_for_operators", [])
        for oper in self._workflow.operators_info:
            if oper["name"] not in show_opers:
                continue
            infos.append(oper)
            print(f"jaha: {oper=}")
        return infos

    # def _update_workflow_with_options(self):
    #     export_options = self.frame_options.workflow_export_options
    #     self._workflow.exporters = self._update_exports_with_zip_archive(export_options)

    def _update_export_directory_in_export_options(self, export_options: list[dict]):
        for opt in export_options:
            if opt.get('name') == 'PolarsZipArchive':
                opt['export_directory'] = self.main_app.zip_directory

    def _update_exports_with_zip_archive(self, export_options: list[dict]) -> list[dict]:
        """Adds ZipPackage export to given export_options. Returns updated list"""
        new_list = []
        zip_archive_exporter_name = 'PolarsZipArchive'
        export_found = False
        for item in export_options:
            if item['name'] == zip_archive_exporter_name:
                item['active'] = True
                item['export_directory'] = str(self.main_app.zip_directory)
                item['open_directory'] = True
                export_found = True
            new_list.append(item)
        print(f'{self.main_app.zip_directory=}')
        if not export_found:
            new_list.append(dict(
                name=zip_archive_exporter_name,
                active=True,
                export_directory=str(self.main_app.zip_directory),
                open_directory=True,
            ))
        return new_list

    def save_export_options(self):
        data = {
            # 'workflow_exports': self.frame_options.workflow_export_options,
            'post_workflow_exports': self.frame_post_options.workflow_export_options}
        saves.user_saves.add_settings(**data)
        saves.user_saves.export_saves()

    def load_export_options(self):
        # options = saves.user_saves.get('workflow_exports', [])
        # self.frame_options.update_workflow_export_options(options)

        options = saves.user_saves.get('post_workflow_exports', [])
        self.frame_post_options.update_workflow_export_options(options)

    def run_exporter(self, **kwargs) -> None:
        if not self._workflow:
            return
        try:
            self._workflow.export(**kwargs)
        except sharkadm_exceptions.DataHolderError:
            self.main_app.show_info('Detta kan endast göras efter du skapat zip-paket')
        finally:
            self.save_export_options()

    def _on_occurrence_valid_added(self, data: dict) -> None:
        self._dialog_messages.append(f"Matchande occurrence_id har "
                                     f"lagts till i data och databas.")

    def _on_occurrence_valid_not_added(self, data: dict) -> None:
        self._dialog_messages.append(f"Matchande occurrence_id har inte lagts till. "
                                     f"Check i boxen om du vill lägga till dessa. "
                                     f"{data['msg']}")

    def _on_db_updated(self, data: dict) -> None:
        self._dialog_messages.append("Occurrencedatabas är uppdaterad! "
                                     "Se till att pusha om du är nöjd med resultatet")




