from pathlib import Path

import flet as ft

from sharkadm.config import sharkadm_config

from sharkadm_zip_creator.flet_app import event
from sharkadm_zip_creator.flet_app import widgets
from sharkadm_zip_creator.flet_app.components.data_source import SourceTypeComponent
from sharkadm_zip_creator.flet_app.components.state import StateComponent
from sharkadm_zip_creator.flet_app.saves import user_saves, UserSavesKeys


@ft.control
class ConfigComponent(ft.Column):
    state: str = None
    source_type: str = None

    def init(self):
        self._config = sharkadm_config
        self._set_config_state(self.state)


        self._state_component = StateComponent(
            on_change=self._on_change_state,
            state=self.state
        ).set_config(self._config)

        self._source_type_component = SourceTypeComponent(
            on_change=self._on_change_source_type,
            source_type=self.source_type
        )

        self._config_root_path = ft.Text(str(self._config.root_dir))


        self._select_zip_directory_button = (
            widgets.DirectoryPickerButton(title="Byt destination",
                                          dialog_title="Väl destinationskatalog för zip-filer",
                                          on_pick=self._on_pick_zip_directory))
        self._zip_target_directory = ft.Text()
        self._zip_target_directory.value = user_saves.get(UserSavesKeys.ZIP_TARGET_DIRECTORY,
                                                          default="",
                                                          state_sensitive=True)

        self.controls = [
            ft.Row([
                self._state_component,
                self._source_type_component,
            ]),
            ft.Row([
                ft.Text("Konfigurationmapp:"),
                self._config_root_path,
            ]),
            ft.Row([
                ft.Text("Zip-paketen hamnar här:"),
                self._zip_target_directory,
                self._select_zip_directory_button
            ]),
        ]

    def _on_pick_zip_directory(self, directory: Path):
        user_saves.set(UserSavesKeys.ZIP_TARGET_DIRECTORY, str(directory), state_sensitive=True)
        self._set_zip_directory(directory)

    def _set_config_state(self, state: str) -> None:
        if state.upper() == "PROD":
            self._config.set_to_prod()
        elif state.upper() == "TEST":
            self._config.set_to_test()

    def _on_change_state(self, data: dict) -> None:
        self._set_config_state(state=data["value"])
        event.post_event(event.Events.CHANGE_STATE, dict(state=data["value"]))
        self._config_root_path.value = str(self._config.root_dir)
        self._zip_target_directory.value = user_saves.get(UserSavesKeys.ZIP_TARGET_DIRECTORY,
                                                          default="",
                                                          state_sensitive=True)
        self._config_root_path.update()
        self._zip_target_directory.update()
        # self._set_zip_directory(user_saves.get(UserSavesKeys.ZIP_TARGET_DIRECTORY, ""))

    def _on_change_source_type(self, data: dict):
        event.post_event(event.Events.CHANGE_SOURCE_TYPE, dict(source_type=data["value"]))

    def _set_zip_directory(self, directory: str | Path) -> None:
        self._zip_target_directory.value = str(directory)
        self._zip_target_directory.update()
        # try:
        #     self._zip_target_directory.update()
        #     print("Setting zip directory!")
        # except RuntimeError:
        #     print("Could not update zip directory!")

    @property
    def zip_target_directory(self) -> Path | None:
        if self._zip_target_directory.value:
            return Path(self._zip_target_directory.value)
        return None