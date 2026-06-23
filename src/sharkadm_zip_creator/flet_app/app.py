import asyncio
import os
import pathlib
import threading
from queue import Queue

import flet as ft
import time
from openpyxl.worksheet import controls
from sharkadm import event as sharkadm_event
from sharkadm.sharkadm_logger import adm_logger, create_xlsx_report
from sharkadm.workflow import SHARKadmWorkflow

from flet_app import app_source
from flet_app.app_source import SourceType
from flet_app.components import ConfigComponent
from flet_app.frames import (
    FrameCreateSingleZip,
    FrameCreateMultipleZip
)
from sharkadm_zip_creator.flet_app import utils

USER_DIR = utils.USER_DIR
SAVES_PATH = utils.SAVES_PATH
from sharkadm_zip_creator.flet_app import saves
from sharkadm_zip_creator.flet_app.saves import user_saves

from sharkadm_zip_creator.flet_app import event
from sharkadm_zip_creator.flet_app.frame_log import FrameLog

from sharkadm_zip_creator.flet_app import app_state

log_buffer = Queue()

# adm_logger.print_on_screen()


class ZipArchiveCreatorGUI(app_state.AppState, app_source.AppSource):
    def __init__(self):
        app_state.AppState.__init__(self)
        app_source.AppSource.__init__(self)
        print(f"{self.state=}")
        print(f"{self.source_type=}")

        user_saves.set_main_app(self)
        user_saves.import_saves()

        self._on_change_state(dict(state=user_saves.get(saves.UserSavesKeys.LATEST_STATE, str(app_state.States.TEST))),
                              update=False)

        self._on_change_source_type(dict(source_type=user_saves.get(saves.UserSavesKeys.LATEST_SOURCE_TYPE, str(app_source.SourceType.SINGLE))),
                              update=False)

        print(f"ZipArchiveCreatorGUI: {threading.current_thread().name=}")

        self.page = None

        self._current_workflow: SHARKadmWorkflow | None = None

        sharkadm_event.subscribe(sharkadm_event.Events.LOG_WORKFLOW, self._on_log_workflow)
        sharkadm_event.subscribe(sharkadm_event.Events.LOG_PROGRESS, self._on_progress)

        # event.subscribe(event.Events.SHOW_INFO, self._on_change_state, prio=5) # test
        event.subscribe(event.Events.SHOW_INFO, self._on_show_info)
        event.subscribe(event.Events.SHOW_ON_LOG_FRAME, self._on_show_on_log_frame)
        event.subscribe(event.Events.SHOW_DIALOG, self._on_show_dialog)
        event.subscribe(event.Events.SHOW_TRANSFORM_DIALOG, self._on_show_transform_dialog)
        event.subscribe(event.Events.RESET_PROGRESS, self.reset_progress)
        event.subscribe(event.Events.CHANGE_STATE, self._on_change_state, prio=5)
        event.subscribe(event.Events.CHANGE_SOURCE_TYPE, self._on_change_source_type, prio=5)

        event.subscribe(event.Events.DISABLE, self.disable, prio=5)
        event.subscribe(event.Events.ENABLE, self.enable, prio=5)

        # print("="*100)
        # print("ZipArchiveCreatorGUI.__init__")
        # print("-"*100)
        # for key, value in event._subscribers.items():
        #     print(f"{key=}")
        #     for p, items in value.items():
        #         print(f"  {p=}")
        #         for item in items:
        #             print(f"    {item=}")
        # print("-" * 100)
        # print("-" * 100)
        # print(f"{list(event.Events)=}")
        # print(f"{event._subscribers.keys()=}")
        # print(f"{event.__file__=}")
        # print(f"{id(event._subscribers)=}")
        # print("APP")
        # print("-" * 100)
        # print("-" * 100)

        self.app = ft.run(self.start)

        self._remove_log_file()

    @property
    def log_file_path(self) -> pathlib.Path:
        return USER_DIR / self.state.log_file_name

    # @property
    # def zip_directory(self) -> str:
    #     return self.frame_config.zip_directory

    def _remove_log_file(self):
        if self.log_file_path.exists():
            os.remove(self.log_file_path)

    def _add_to_log_file(self, text: str) -> None:
        with open(self.log_file_path, 'a', encoding='cp1252') as fid:
            fid.write(f'{text}\n')

    def start(self, page: ft.Page):
        self.page = page
        self.page.title = self.state.app_title
        self.page.window.height = 1200
        self.page.window.width = 2200
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window.on_event = self._on_app_event

        # self.page.add(ft.Column([
        #     ft.Text("Testar"),
        #     ft.Text("Testar två rader"),
        #     ConfigComponent()
        # ]))
        # return

        # self.config_component = ConfigComponent(
        #     state=str(self.state.state),
        #     source_type=str(self.source_type.source),
        # )
        # self.page.add(self.config_component)

        self.create_layout()

        # start UI log loop
        self.page.run_task(self._log_loop)

        # self.page.theme_mode = ft.ThemeMode.LIGHT
        # page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)
        # page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)
        # self._build()
        # self._add_controls_to_save()
        # self.import_user_saves()
        # config_saves.import_saves(self)
        # self.frame_config.show_env_message()
        # self.frame_config.check_paths()

    async def _log_loop(self):
        while True:
            try:
                data = log_buffer.get_nowait()
            except Exception:
                await asyncio.sleep(0.05)
                continue

            level = data.get("level", "").upper()
            msg = data.get("msg", "")

            self._info_text.value = f"{level}: {msg}"
            self.page.update()

    def _on_change_state(self, data: dict, update: bool = True) -> None:
        print("CHANGING STATE")
        if data.get('state') == app_state.States.PROD:
            self.state.set_to_prod()
        elif data.get('state') == app_state.States.TEST:
            self.state.set_to_test()
        self._latest_state = self.state.state
        user_saves.set(saves.UserSavesKeys.LATEST_STATE, str(self._latest_state))
        # user_saves.import_saves()
        if update:
            self.update_layout()

    def _on_change_source_type(self, data: dict, update: bool = True) -> None:
        if data.get('source_type') == app_source.SourceType.SINGLE:
            self.source_type.set_to_single()
        elif data.get('source_type') == app_source.SourceType.MULTIPLE:
            self.source_type.set_to_multiple()
        self._latest_source_type = self.source_type.source
        user_saves.set(saves.UserSavesKeys.LATEST_SOURCE_TYPE, str(self._latest_source_type))
        # user_saves.import_saves()
        if update:
            self.update_layout()

    def disable(self, *args, **kwargs):
        self.config_component.disabled = True
        self.config_component.update()

    def enable(self, *args, **kwargs):
        self.config_component.disabled = False
        self.config_component.update()

    def create_layout(self):
        print("Creating Layout in main app!")
        # self.page.controls.clear()
        # self.page.controls = self.page.controls[:1]
        # # self.update_page()
        # event.clear_subscribers()
        self._build_components()
        self._build_layout()
        self._update_layout()
        self.update_page()

    def update_layout(self):
        print("Updating Layout in main app!")
        self._update_layout()
        self.update_page()

    def _build_transform_dialog(self):
        self._alert_transform_levels = dict()
        controls = []
        for level in (adm_logger.DEBUG, adm_logger.INFO, adm_logger.WARNING):
            self._alert_transform_levels[level] = ft.Checkbox(label=str(level).upper())
            controls.append(self._alert_transform_levels[level])
        self._alert_transform_levels[adm_logger.WARNING].value = True
        level_checkboxes = ft.Column(controls)

        self._transform_dialog_title = ft.Text()
        self._transform_dialog_text = ft.Text(
            selectable=True,
        )

        self._transform_dlg = ft.AlertDialog(
            modal=True,
            title=self._transform_dialog_title,

            # ALLT innehåll läggs här
            content=ft.Container(
                content=ft.Column(
                    [
                        # SCROLLBAR DEL
                        ft.Container(
                            width=400,
                            expand=True,
                            border=ft.Border.all(1),

                            content=ft.ListView(
                                controls=[
                                    self._transform_dialog_text
                                ],
                                expand=True,
                                spacing=10,
                                auto_scroll=False,
                            ),
                        ),

                        ft.Divider(),

                        # FAST DEL
                        ft.Text("Välj loggnivåer:"),

                        level_checkboxes,

                        ft.Row(
                            [
                                ft.Button(
                                    "Öppna log",
                                    on_click=self._on_ok_create_transform_dialog_log,
                                ),
                                ft.Button(
                                    "Stäng",
                                    on_click=self._on_close_transform_dialog,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    expand=True,
                )
                # content=ft.Column(
                #     [
                #         self._transform_dialog_text,
                #         ft.Divider(),
                #         ft.Text("Välj loggnivåer:"),
                #         level_checkboxes,
                #         ft.Button(
                #             "Öppna log",
                #             on_click=self._on_ok_create_transform_dialog_log,
                #         ),
                #     ],
                #     scroll=ft.ScrollMode.AUTO,  # <- gör innehållet skrollbart
                #     tight=True,
                # ),
                # width=400,
                # height=300,  # viktigt för att scroll ska fungera
                # padding=10,
            ),

            # on_dismiss=self._on_close_transform_dialog,
        )

    def _on_ok_create_transform_dialog_log(self, e):
        # self._transform_dlg.open = False
        # self.page.update()
        self._on_close_transform_dialog()
        if not self._current_workflow:
            return
        print(f"{[str(level) for level, wid in self._alert_transform_levels.items() if wid.value]=}")
        create_xlsx_report(
            log_filter=dict(levels=[str(level) for level, wid in self._alert_transform_levels.items() if wid.value]),
            open_file=True,
        )

    def _on_close_transform_dialog(self, e = None):
        self._transform_dlg.open = False
        self.page.update()

    def _build_general_dialog(self) -> None:
        self._dialog_title = ft.Text()
        self._dialog_text = ft.Text()

        self._dlg = ft.AlertDialog(
            title=self._dialog_title,
            content=self._dialog_text,
            alignment=ft.Alignment.CENTER,
            on_dismiss=self._on_close_dialog,
            title_padding=ft.Padding.all(25),
        )

    def _build_components(self):
        print("BUILDING")
        self._build_general_dialog()
        self._build_transform_dialog()

        self.config_component = ConfigComponent(
            state=str(self.state.state),
            source_type=str(self.source_type.source),
        )


        self._info_text = ft.Text("Det här är infotext....som kommer att ändras när det händer något...", bgcolor='gray')
        print(f"_build_components: {id(self._info_text)=}")

        self._progress_text = ft.Text()
        self._progress_bar = ft.ProgressBar(width=400, value=0)

        self._progress_row = ft.Row([
            self._progress_bar,
            self._progress_text,
        ])

        self.frame_log = FrameLog()
        if hasattr(self, "_frame_create_single_zip"):
            # print(f"1: {self._frame_create_single_zip=}")
            print(f"1: {id(self._frame_create_single_zip)=}")
        self._frame_create_single_zip = FrameCreateSingleZip(visible=self.source_type.source == SourceType.SINGLE, main_app=self)
        self._frame_create_multiple_zip = FrameCreateMultipleZip(visible=self.source_type.source == SourceType.MULTIPLE)
        # if hasattr(self, "_frame_create_single_zip"):
        #     # print(f"2: {self._frame_create_single_zip=}")
        #     print(f"2: {id(self._frame_create_single_zip)=}")

        self._frame_create_single_zip.state = self.state
        self._frame_create_multiple_zip.state = self.state

        self._tabs = ft.Tabs(
            length=2,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Skapa ZIP-paket"),
                            ft.Tab(label="Log", icon=ft.Icons.EDIT_DOCUMENT),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            # ft.Container(
                            #     expand=True,
                            #     content=self._frame_create_single_zip,
                            # ),
                            ft.Container(
                            #     alignment=ft.Alignment.CENTER,
                                content=ft.Column([
                                    self._frame_create_single_zip,
                                    self._frame_create_multiple_zip,
        # self._frame_create_multiple_zip,
                                ], expand=True),
                                expand=True,
                            ),
                            ft.Container(
                                alignment=ft.Alignment.CENTER,
                                content=self.frame_log,
                                expand=True,
                            ),
                        ],
                    ),
                ],
            ),
        )


    def _build_layout(self):
        print("BUILDING LAYOUT")
        self._main_column = ft.Column([
            self.config_component,
            ft.Divider(),
            self._tabs,
            ft.Divider(),
            self._info_text,
            self._progress_row,
        ], expand=True)
        self.page.add(self._main_column)

    def _update_layout(self):
        self.page.title = self.state.app_title
        self._frame_create_single_zip.visible = self.source_type.is_visible(app_source.VISIBLE.SINGLE_ZIP)
        self._frame_create_multiple_zip.visible = self.source_type.is_visible(app_source.VISIBLE.MULTIPLE_ZIP)

    def _on_progress(self, data: dict) -> None:
        current = data.get('current', 1)
        total = data.get('total', 1)
        if current > total:
            current = total

        msg = data.get('msg') or f'{data.get("title", "")} ({current} / {total})'
        self._progress_text.value = msg
        self._progress_bar.value = int(10 * current / total) / 10
        self._progress_text.update()
        self._progress_bar.update()

    def reset_progress(self, data: dict | None = None) -> None:
        self._progress_text.value = ''
        self._progress_bar.value = 0
        self._progress_text.update()
        self._progress_bar.update()

    def _on_show_dialog(self, data: dict) -> None:
        title = data.get("title", "Det här är något som kan vara bra att veta")
        msg = data.get("msg", "Här borde det stå något annat förmodligen...")
        self._on_show_info(msg)
        self._dialog_title.value = title
        self._dialog_text.value = msg
        self._open_dlg(self._dlg)

    def _on_show_transform_dialog(self, data: dict) -> None:
        title = data.get("title", "Det här är något som kan vara bra att veta")
        msg = data.get("msg", "Här borde det stå något annat förmodligen...")
        self._current_workflow = data.get("workflow")
        self._transform_dialog_title.value = title
        self._transform_dialog_text.value = msg
        import nodc_station
        print(f"{nodc_station.get_matching_stations.cache_info()=}")
        self._open_dlg(self._transform_dlg)

    def _on_show_info(self, msg: str = '') -> None:
        self._add_to_log_file(msg)
        self.frame_log.add_text(msg)
        self._info_text.value = msg
        self._info_text.update()

    def _on_show_on_log_frame(self, msg: str = '') -> None:
        self.frame_log.add_text(msg)

    def _on_log_workflow(self, data: dict) -> None:
        level = data.get('level')
        level = level.upper()
        text = f'{level}: {data.get("msg")}'
        self._on_show_info(text)

    def _open_dlg(self, dlg, *args):
        self.page.show_dialog(dlg)

    def _on_close_dialog(self, *args):
        print("Closing dialog")

    def _on_app_event(self, *args):
        self._save_layout()
    #
    def update_page(self):
        print("update_page")
        self.page.update()

    #
    #
    # def _on_show_info(self, msg: str = '') -> None:
    #     self._add_to_log_file(msg)
    #     self.frame_log.add_text(msg)
    #     self._info_text.value = msg
    #     self._info_text.update()
    #
    # def update_source(self, path: str, update_latest_source: bool = True) -> None:
    #     try:
    #         self.disable_frames()
    #
    #         data_holder = get_polars_data_holder(path)
    #         self._on_show_info('Data holder loaded')
    #
    #         print(f'{data_holder.data_type_internal=}')
    #
    #         # Validate
    #         wflow = workflow.get_dv_validation_workflow_for_data_type(data_holder.data_type_internal)
    #         self.frame_validate.set_workflow(wflow, data_holder.data_type)
    #         self._add_source_to_workflow(wflow)
    #         self._on_show_info('Workflow for validation is set up')
    #
    #         wflow.save_config(utils.USER_DIR / 'test_validate_workflow.yaml')
    #
    #         # Create
    #         wflow = workflow.get_dv_workflow_for_data_type(data_holder.data_type_internal)
    #         self.frame_create_zip.set_workflow(wflow, data_holder.data_type)
    #         self._add_source_to_workflow(wflow)
    #         self._on_show_info('Workflow for creation is set up')
    #
    #         wflow.save_config(utils.USER_DIR / 'test_create_workflow.yaml')
    #
    #         # if not self.frame_config.env:
    #         #     self.frame_config.env =
    #
    #     except Exception:
    #         raise
    #     finally:
    #         self.enable_frames()
    #
    # def _add_source_to_workflow(self, wflow: workflow.SHARKadmWorkflow):
    #     path = self.frame_source.source_path
    #     if not path:
    #         wflow.set_data_sources()
    #     else:
    #         wflow.set_data_sources(path)
    #
    # def import_user_saves(self):
    #     config_saves.import_saves(self)
    #     self.frame_source.import_user_saves()
    #     self.page.window.width = user_saves.get("page_window_width")
    #     self.page.window.height = user_saves.get("page_window_height")
    #     self.update_page()
    #
    def _save_layout(self):
        user_saves.add_settings(
            page_window_width=self.page.window.width,
            page_window_height=self.page.window.height,
        )

        # import asyncio
        # import flet as ft
        #
        # class Countdown(ft.Text):
        #     def __init__(self, seconds):
        #         super().__init__()
        #         self.seconds = seconds
        #
        #     def did_mount(self):
        #         self.running = True
        #         self.page.run_task(self.update_timer)
        #
        #     def will_unmount(self):
        #         self.running = False
        #
        #     async def update_timer(self):
        #         while self.seconds and self.running:
        #             mins, secs = divmod(self.seconds, 60)
        #             self.value = "{:02d}:{:02d}".format(mins, secs)
        #             self.update()
        #             await asyncio.sleep(1)
        #             self.seconds -= 1
        #
        # def main(page: ft.Page):
        #     page.add(Countdown(120), Countdown(60))
        #
        # ft.run(main)
        # user_saves.export_saves()
    #
    # def _add_controls_to_save(self):
    #     pass

        # creator_saves.add_control('page_add_archive._option_update_zip_archives', self.page_add_archive._option_update_zip_archives)
        # creator_saves.add_control('page_add_archive._option_copy_zip_archives_to_sharkdata', self.page_add_archive._option_copy_zip_archives_to_sharkdata)
        # creator_saves.add_control('page_add_archive._option_trigger_dataset_import', self.page_add_archive._option_trigger_dataset_import)
        #
        # creator_saves.add_control('page_remove_archive._option_create_remove_file', self.page_remove_archive._option_create_remove_file)
        # creator_saves.add_control('page_remove_archive._option_trigger_remove_file', self.page_remove_archive._option_trigger_remove_file)
        #
        # creator_saves.add_control('page_config._option_copy_config_to_sharkdata', self.page_config._option_copy_config_to_sharkdata)
        # creator_saves.add_control('page_config._option_trigger_config_import', self.page_config._option_trigger_config_import)


