import threading
from dataclasses import dataclass
from typing import Any

import flet as ft
from sharkadm import event as sharkadm_event
from sharkadm import sharkadm_exceptions, workflow
from sharkadm.data import get_polars_data_holder
from sharkadm.sharkadm_logger import adm_logger

from sharkadm_zip_creator.flet_app import event
from sharkadm_zip_creator.flet_app.components import (
    PostWorkflowExportOptionsComponent,
    SingleDataSourceComponent,
    WorkflowOptionsComponent,
)
from sharkadm_zip_creator.flet_app.components.operators_list import ListOperatorsComponent
from sharkadm_zip_creator.flet_app.saves import user_saves


# @ft.control
@dataclass
class FrameCreateSingleZip(ft.Container):
    expand: bool = True
    main_app: Any = None

    def init(self):
        self._transformation_logs: list[str] = []
        sharkadm_event.subscribe(
            sharkadm_event.Events.LOG_TRANSFORMATION, self._on_log_transformation
        )

        self._workflow: workflow.SHARKadmWorkflow | None = None
        self._workflow_config_path = ft.Text()
        config_path_row = ft.Row(
            [ft.Text("Konfigurationsfil:"), self._workflow_config_path], expand=True
        )
        self.data_source = SingleDataSourceComponent()
        self._show_operators_info_switch = ft.Switch(
            label="Visa operationer", on_change=self._on_change_show_operators_info_switch
        )
        self.operators_component = ListOperatorsComponent()
        self.workflow_options_component = WorkflowOptionsComponent()
        self.post_export_options_component = PostWorkflowExportOptionsComponent()
        self.button_create_zip = ft.Button("Skapa zip-paket", on_click=self.on_create_zip)

        self.operators_component.visible = False

        event.subscribe(
            event.Events.CHANGE_SINGLE_DATA_SOURCE, self._on_change_source, prio=75
        )

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
                                content=ft.Column(
                                    [
                                        self.workflow_options_component,
                                    ],
                                    expand=True,
                                ),
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

        self.content = ft.Column(
            [
                self.data_source,
                config_path_row,
                self._show_operators_info_switch,
                ft.Row(
                    [
                        self.operators_component,
                        self.workflow_options_component,
                        self.post_export_options_component,
                    ],
                    expand=True,
                ),
                self.button_create_zip,
            ],
            expand=True,
        )

    def _on_log_transformation(self, data: dict[str, Any]) -> None:
        if data.get("level") not in [
            adm_logger.WARNING,
            adm_logger.ERROR,
            adm_logger.CRITICAL,
        ]:
            return
        msg = data.get("msg", "")
        event.post_event(event.Events.SHOW_ON_LOG_FRAME, msg)
        self._transformation_logs.append(msg)

    def _on_change_source(self, data: dict):
        path = data["path"]
        data_holder = get_polars_data_holder(path)
        wflow = workflow.get_dv_workflow_for_data_type(data_holder.data_type_internal)
        wflow.set_data_sources(path)
        self._set_workflow(wflow)

    def _on_change_show_operators_info_switch(self, e: ft.Event[ft.Switch]):
        self.operators_component.visible = self._show_operators_info_switch.value
        self.operators_component.update()

    def _set_workflow(self, wflow: workflow.SHARKadmWorkflow) -> None:
        self._workflow = wflow
        print("-" * 50)
        print(f"{self._workflow.path=}")
        self._workflow_config_path.value = str(self._workflow.path)
        self._workflow_config_path.update()

        self._load_export_options()

        self.operators_component.set_workflow(wflow)
        self.workflow_options_component.set_workflow(wflow)
        self.post_export_options_component.set_workflow(wflow)

    def save_export_options(self):
        data = {
            "post_workflow_exports":
                self.post_export_options_component.workflow_export_options
        }
        user_saves.add_settings(**data)

    def _load_export_options(self):
        options = user_saves.get("post_workflow_exports", [])
        self.post_export_options_component.update_workflow_export_options(options)

    def _start_workflow(self):
        def run():
            result = None
            error = None

            try:
                import time

                t0 = time.perf_counter()
                result = self._workflow.start_workflow()
                print(f"{time.perf_counter()-t0=}")
            except Exception as e:
                error = e

            finally:
                self.page.run_task(self._on_workflow_done, result, error)

        self._workflow.update_operators(self.workflow_options_component.workflow_options)
        threading.Thread(target=run, daemon=True).start()

    async def _on_workflow_done(self, result, error):
        if error:
            event.post_event(event.Events.SHOW_DIALOG, str(error))
            self._enable()
            return

        event.post_event(event.Events.SHOW_INFO, str(result))
        self._enable()

        data = dict()
        if error:
            data["title"] = "Något gick fel..."
            data["msg"] = str(error)
        elif result:
            data["title"] = "Något kanske gick fel..."
            data["msg"] = str(result)
        else:
            if self._transformation_logs:
                data["title"] = "Allt klart! Men, ta en titt på det här!"
                data["msg"] = "\n".join(self._transformation_logs)
                data["logs"] = self._transformation_logs
                data["workflow"] = self._workflow
            else:
                data["title"] = "Allt klart!"
                data["msg"] = data["title"]
        event.post_event(event.Events.SHOW_TRANSFORM_DIALOG, data)
        self.main_app.reset_progress()
        # saves.config_saves.export_saves()
        self.save_export_options()

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
        self._transformation_logs = []
        print("on_create_zip!")
        if not self._workflow:
            event.post_event(event.Events.SHOW_INFO, dict(title="Ingen fil vald!"))
            return
        if not self.data_source.source_path:
            event.post_event(
                event.Events.SHOW_INFO, dict(title="Sökväg till zip-paketen saknas!")
            )
            return
        try:
            self._disable()
            self._start_workflow()
        except Exception as e:
            failed_msg = str(e)
            print(f"{failed_msg=}")

    def run_exporter(self, **kwargs) -> None:
        if not self._workflow:
            return
        try:
            self._workflow.export(**kwargs)
        except sharkadm_exceptions.DataHolderError:
            self.main_app.show_info(
                dict(title="Detta kan endast göras efter du skapat zip-paket")
            )
        finally:
            self.save_export_options()

    def update_layout(self):
        self.operators_component.set_height()
        self.workflow_options_component.set_height()
        self.post_export_options_component.set_height()
