from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import flet as ft


@dataclass
class SingleFilePickerButton(ft.Row):
    title: str = ""
    on_pick: Callable = None
    initial_directory: str = ""
    dialog_title: str = ""
    allowed_extensions: list | None = None

    def init(self):
        self.button = ft.Button(
            self.title, icon=ft.Icons.UPLOAD_FILE, on_click=self.handle_pick_file
        )

        self.controls = [
            self.button,
        ]

    async def handle_pick_file(self, e: ft.Event[ft.Control]):
        file = await ft.FilePicker().pick_files(
            allow_multiple=False,
            initial_directory=self.initial_directory,
            allowed_extensions=self.allowed_extensions or [],
            dialog_title=self.dialog_title or self.title,
        )
        if not file:
            return
        path = Path(file[0].path)
        self.initial_directory = str(path.parent)
        if self.on_pick:
            self.on_pick(path)


@dataclass
class MultipleFilePickerButton(ft.Row):
    title: str = ""
    on_pick: Callable = None
    dialog_title: str = ""
    allowed_extensions: list | None = None

    def init(self):
        self.button = ft.Button(
            self.title, icon=ft.Icons.UPLOAD_FILE, on_click=self.handle_pick_file
        )

        self.controls = [
            self.button,
        ]

    async def handle_pick_file(self, e: ft.Event[ft.Control]):
        files = await ft.FilePicker().pick_files(
            allow_multiple=True,
            allowed_extensions=self.allowed_extensions or [],
            dialog_title=self.dialog_title or self.title,
        )
        if not files:
            return
        if self.on_pick:
            self.on_pick([Path(file.path) for file in files])


@dataclass
class DirectoryPickerButton(ft.Row):
    title: str = ""
    initial_directory: str = ""
    on_pick: Callable = None
    dialog_title: str = ""

    def init(self):
        self.button = ft.Button(
            self.title, icon=ft.Icons.UPLOAD_FILE, on_click=self.handle_get_directory_path
        )

        self.controls = [
            self.button,
        ]

    async def handle_get_directory_path(self, e: ft.Event[ft.Button]):
        directory = await ft.FilePicker().get_directory_path(
            dialog_title=self.dialog_title,
            initial_directory=self.initial_directory,
        )
        if not directory:
            return
        self.initial_directory = directory
        if self.on_pick:
            self.on_pick(Path(directory))

    # async def handle_save_file(self, e: ft.Event[ft.Control]):
    #     save_file_path.value = await ft.FilePicker().save_file()
    #
