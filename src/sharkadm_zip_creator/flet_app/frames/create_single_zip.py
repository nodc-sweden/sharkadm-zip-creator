import threading
from dataclasses import dataclass
from typing import Any

import flet as ft
from sharkadm import workflow, sharkadm_exceptions
from sharkadm.data import get_polars_data_holder

from sharkadm_zip_creator.flet_app import event, utils, saves
from flet_app.components import WorkflowOptionsComponent, SingleDataSourceComponent, PostWorkflowExportOptionsComponent
from flet_app.components.operators_list import ListOperatorsComponent
from flet_app.saves import user_saves


# @ft.control
@dataclass
class FrameCreateSingleZip(ft.Container):
    expand: bool = True
    main_app: Any = None

    def init(self):
        self._workflow: workflow.SHARKadmWorkflow | None = None
        self._workflow_config_path = ft.Text()
        config_path_row = ft.Row([
            ft.Text('Konfigurationsfil:'),
            self._workflow_config_path
        ], expand=True)
        self.data_source = SingleDataSourceComponent()
        self.operators_component = ListOperatorsComponent()
        self.workflow_options_component = WorkflowOptionsComponent()
        self.post_export_options_component = PostWorkflowExportOptionsComponent()
        self.button_create_zip = ft.Button(f"Skapa zip-paket", on_click=self.on_create_zip)

        event.subscribe(event.Events.CHANGE_SINGLE_DATA_SOURCE, self._on_change_source)

        self._option_tabs = ft.Tabs(
            length=2,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Under körning"),
                            ft.Tab(label="Efter körning"),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            ft.Container(
                                content=ft.Column([
                                    self.workflow_options_component,
                                ], expand=True),
                                expand=True,
                            ),
                            ft.Container(
                                alignment=ft.Alignment.CENTER,
                                content=self.post_export_options_component,
                                expand=True,
                            ),
                        ],
                    ),
                ],
            ),
        )

        self.content = ft.Column([
            config_path_row,
            self.data_source,
            ft.Row([
                self.operators_component,
                self.workflow_options_component,
                self.post_export_options_component,
            ], expand=True),
            self.button_create_zip,

        ], expand=True)

        # self.controls = [
        #     config_path_row,
        #     self.data_source,
        #     ft.Container(
        #         expand=True,
        #         bgcolor=ft.Colors.RED,
        #         content=ft.Column([
        #             ft.Row([
        #                 self.operators_component,
        #                 # self.operators_component,
        #                 self._option_tabs,
        #             ],
        #                 expand=True,
        #                 # vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        #                 alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        #             ),
        #             self.button_create_zip
        #         ])
        #
        #     )
        #
        # ]

    def _on_change_source(self, data: dict):
        # Disable stuff
        # print()
        # print(f"{self.page.controls=}")
        # for cont in self.page.controls:
        #     print(f"{cont=}")
        # self._reset_workflow()
        path = data["path"]
        data_holder = get_polars_data_holder(path)
        wflow = workflow.get_dv_workflow_for_data_type(data_holder.data_type_internal)
        wflow.set_data_sources(path)
        self._set_workflow(wflow)


    # def _reset_workflow(self) -> None:
    #     self.operators_component.reset()
    #     self.workflow_options_component.reset()
    #     self.post_export_options_component.reset()


    def _set_workflow(self, wflow: workflow.SHARKadmWorkflow) -> None:
        self._workflow = wflow
        self._workflow_config_path.value = str(self._workflow.path)

        # wflow.save_config(utils.USER_DIR / 'test_create_workflow.yaml')
        self._load_export_options()

        self.operators_component.set_workflow(wflow)
        self.workflow_options_component.set_workflow(wflow)
        self.post_export_options_component.set_workflow(wflow)

    def save_export_options(self):
        data = {
            # 'workflow_exports': self.frame_options.workflow_export_options,
            'post_workflow_exports': self.post_export_options_component.workflow_export_options}
        user_saves.add_settings(**data)
        # user_saves.set_main_app(self.main_app)
        user_saves.export_saves()

    def _load_export_options(self):
        options = user_saves.get('post_workflow_exports', [])
        self.post_export_options_component.update_workflow_export_options(options)

    # def _start_workflow(self) -> Any:
    #     return threading.Thread(
    #         target=self._workflow.start_workflow,
    #         daemon=True
    #     ).start()

    # def _start_workflow(self, on_done=None) -> None:
    #     def run():
    #         try:
    #             self._workflow.start_workflow()
    #         finally:
    #             if on_done:
    #                 on_done()
    #
    #     threading.Thread(target=run, daemon=True).start()

    def _start_workflow(self):
        def run():
            result = self._workflow.start_workflow()
            self.page.run_task(self._on_workflow_done, result)

        threading.Thread(target=run, daemon=True).start()

    async def _on_workflow_done(self, result):
        self._enable()

        if result:
            print("Workflow finished with result:", result)
            # visa dialog eller logga
            event.post_event(event.Events.SHOW_INFO, str(result))

        # self.page.update()

    def _disable(self):
        event.post_event(event.Events.DISABLE, dict())
        self.data_source.disabled = True
        self.data_source.update()
        self.button_create_zip.disabled = True
        self.button_create_zip.update()

    def _enable(self):
        event.post_event(event.Events.ENABLE, dict())
        self.data_source.disabled = False
        self.data_source.update()
        self.button_create_zip.disabled = False
        self.button_create_zip.update()

    def on_create_zip(self, e: ft.Event[ft.Button]) -> None:
        self._dialog_messages = []
        print("on_create_zip!")
        # print()
        # print("="*100)
        # print(f"{event._subscribers=}")
        # print("-" * 100)
        # for key, value in event._subscribers.items():
        #     print(f"{key=}: {value=}")
        # print("-" * 100)
        # print()
        # self.main_app._on_show_info(msg)
        failed_msg = ""
        if not self._workflow:
            event.post_event(event.Events.SHOW_INFO, "Ingen fil vald!")
            return
        if not self.data_source.source_path:
            event.post_event(event.Events.SHOW_INFO, "Sökväg till zip-paketen saknas!")
            return
        try:
            self._disable()
            info = self._start_workflow()
            if info:
                failed_msg = str(info.exception)
            else:
                saves.config_saves.export_saves()
                self.save_export_options()
        except Exception as e:
            failed_msg = str(e)
            pass
            # raise
        # self._enable()
        self.main_app.reset_progress()
        if failed_msg:
            event.post_event(event.Events.SHOW_DIALOG, failed_msg)
        else:
            if self._dialog_messages:
                msg = f"Allt klart!\n" + "\n".join(self._dialog_messages)
                event.post_event(event.Events.SHOW_DIALOG, msg)
            else:
                event.post_event(event.Events.SHOW_DIALOG, "Allt klart!")
        print("Creating zip!")
        print(f"{self.page=}")
        print(f"{self.main_app=}")
        print(f"{self.main_app.state=}")

    def run_exporter(self, **kwargs) -> None:
        if not self._workflow:
            return
        try:
            self._workflow.export(**kwargs)
        except sharkadm_exceptions.DataHolderError:
            self.main_app.show_info('Detta kan endast göras efter du skapat zip-paket')
        finally:
            self.save_export_options()

