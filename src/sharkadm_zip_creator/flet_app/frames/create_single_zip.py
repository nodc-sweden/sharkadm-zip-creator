import threading
import traceback
from dataclasses import dataclass
from typing import Any

import flet as ft
from sharkadm import event as sharkadm_event
from sharkadm import sharkadm_exceptions, workflow
from sharkadm.data import get_polars_data_holder

from sharkadm_zip_creator.flet_app import event
from sharkadm_zip_creator.flet_app.components import (
    PostWorkflowExportOptionsComponent,
    SingleDataSourceComponent,
    WorkflowOptionsComponent,
)
from sharkadm_zip_creator.flet_app.components.operators_list import (
    ListOperatorsComponent,
)
from sharkadm_zip_creator.flet_app.language import get_text
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
            [ft.Text(get_text("configuration_file")), self._workflow_config_path],
            expand=True,
            # [ft.Text("Konfigurationsfil:"), self._workflow_config_path], expand=True
        )
        self.data_source = SingleDataSourceComponent()
        self._show_operators_info_switch = ft.Switch(
            label=get_text("show_operations"),
            on_change=self._on_change_show_operators_info_switch,
        )
        self.operators_component = ListOperatorsComponent()
        self.workflow_options_component = WorkflowOptionsComponent()
        self.post_export_options_component = PostWorkflowExportOptionsComponent()
        self.button_create_zip = ft.Button(
            get_text("create_zip_package"), on_click=self.on_create_zip
        )
        self.button_open_result = ft.Button(
            get_text("open_result"),
            on_click=self.on_open_result,
            visible=False,
        )

        self.operators_component.visible = False

        event.subscribe(
            event.Events.CHANGE_SINGLE_DATA_SOURCE, self._on_change_source, prio=75
        )

        event.subscribe(event.Events.RUN_EXPORTER, self._run_exporter)

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
                self.button_open_result,
            ],
            expand=True,
        )

    def _on_log_transformation(self, data: dict[str, Any]) -> None:
        # if data.get("level") not in [
        #     adm_logger.WARNING,
        #     adm_logger.ERROR,
        #     adm_logger.CRITICAL,
        # ]:
        #     return
        # level = data.get("level", "").upper()
        msg = data.get("msg", "")
        level = data.get("level", "")
        event.post_event(event.Events.SHOW_ON_LOG_FRAME, msg)
        self._transformation_logs.append(f"{level}: {msg}")
        # self._transformation_logs.append(f"{level}: {msg}")

    def _on_change_source(self, data: dict):
        self.button_open_result.visible = False
        self.button_open_result.update()
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
        self._workflow_config_path.value = str(self._workflow.path)
        self._workflow_config_path.update()

        self._load_export_options()

        self.operators_component.set_workflow(wflow)
        self.workflow_options_component.set_workflow(wflow)
        self.post_export_options_component.set_workflow(wflow)

    def save_export_options(self):
        data = {
            "post_workflow_exports":
                self.post_export_options_component.workflow_export_options,
        }
        user_saves.add_settings(**data)

    def _load_export_options(self):
        options = user_saves.get("post_workflow_exports", [])
        self.post_export_options_component.update_workflow_export_options(options)

    def _start_workflow(self):
        def run():
            # self.result = None
            # self.error = None

            self.main_app._current_workflow = self._workflow

            try:
                import time

                t0 = time.perf_counter()
                self.result = self._workflow.start_workflow()
                print(f"run: {id(self.result)=}")
                print(f"{time.perf_counter()-t0=}")
            except Exception as e:
                self.error = e

            finally:
                self.page.run_task(self._on_workflow_done, self.result, self.error)

        # print()
        # print("=" * 100)
        # print(f"{self.workflow_options_component.workflow_options=}")
        # print()
        self._workflow.update_operators(self.workflow_options_component.workflow_options)
        self._workflow.update_exporters(self.workflow_options_component.workflow_options)
        exp = dict(
            name="PolarsZipArchive",
            export_directory=str(self.main_app.config_component.zip_target_directory),
        )
        self._workflow.update_exporters([exp])
        self.result = None
        print(f"_start_workflow: {id(self.result)=}")
        self.error = None
        threading.Thread(target=run, daemon=True).start()

    async def _on_workflow_done(self, result, error):
        if error:
            event.post_event(event.Events.SHOW_DIALOG, str(error))
            self._enable()
            return

        event.post_event(event.Events.SHOW_INFO, str(result))
        self._enable()

        self._open_transform_dialog()

        # data = dict()
        # if error:
        #     data["title"] = get_text("something_went_wrong")
        #
        #     data["msg"] = str(error)
        # elif result:
        #     data["title"] = get_text("something_maybe_went_wrong")
        #     data["msg"] = str(result)
        # else:
        #     if self._transformation_logs:
        #         data["title"] = get_text("all_done_but")
        #         data["msg"] = "\n".join(self._transformation_logs)
        #         data["logs"] = self._transformation_logs
        #         data["workflow"] = self._workflow
        #     else:
        #         data["title"] = get_text("all_done")
        #         data["msg"] = data["title"]
        # event.post_event(event.Events.SHOW_TRANSFORM_DIALOG, data)
        self.main_app.reset_progress()
        # saves.config_saves.export_saves()
        self.save_export_options()

    def _open_transform_dialog(self):
        data = dict()
        if self.error:
            data["title"] = get_text("something_went_wrong")

            data["msg"] = str(self.error)
        elif self.result:
            data["title"] = get_text("something_maybe_went_wrong")
            data["msg"] = str(self.result)
        else:
            if self._transformation_logs:
                data["title"] = get_text("all_done_but")
                data["msg"] = "\n".join(self._transformation_logs)
                data["logs"] = self._transformation_logs
                data["workflow"] = self._workflow
            else:
                data["title"] = get_text("all_done")
                data["msg"] = data["title"]
        event.post_event(event.Events.SHOW_TRANSFORM_DIALOG, data)

    def _disable(self):
        event.post_event(event.Events.DISABLE, dict())
        self.data_source.disabled = True
        self.data_source.update()
        self.button_create_zip.disabled = True
        self.button_create_zip.update()
        self.button_open_result.disabled = True
        self.button_open_result.visible = True
        self.button_open_result.update()

    def _enable(self):
        event.post_event(event.Events.ENABLE, dict())
        self.data_source.disabled = False
        self.data_source.update()
        self.button_create_zip.disabled = False
        self.button_create_zip.update()
        self.button_open_result.disabled = False
        self.button_open_result.update()

    def on_create_zip(self, e: ft.Event[ft.Button]) -> None:
        self._transformation_logs = []
        print("on_create_zip!")
        if not self._workflow:
            event.post_event(event.Events.SHOW_INFO, get_text("no_file_selected"))
            return
        if not self.data_source.source_path:
            event.post_event(
                event.Events.SHOW_INFO,
                get_text("missing_path_to_zip_packages"),
            )
            return
        try:
            self._disable()
            event.post_event(event.Events.ON_START_WORKFLOW, None)
            self._start_workflow()
        except Exception as e:
            event.post_event(
                event.Events.SHOW_DIALOG,
                dict(
                    title=get_text("something_went_wrong"),
                    msg=f"{e}: \n\n{traceback.format_exc()}",
                ),
            )
        finally:
            event.post_event(event.Events.ON_END_WORKFLOW, None)

    def on_open_result(self, e: ft.Event[ft.Button]) -> None:
        print(f"on_open_result: {id(self.result)=}")
        print(f"on_open_result: {self.result=}")
        if not self._transformation_logs:
            return
        self._open_transform_dialog()

    def _run_exporter(self, kwargs) -> None:
        if not self._workflow:
            return
        try:
            self._workflow.export(**kwargs)
        except sharkadm_exceptions.DataHolderError:
            self.main_app.show_info(dict(title=get_text("only_after_zip_creation")))
        finally:
            self.save_export_options()

    def update_layout(self):
        self.operators_component.set_height()
        self.workflow_options_component.set_height()
        self.post_export_options_component.set_height()
