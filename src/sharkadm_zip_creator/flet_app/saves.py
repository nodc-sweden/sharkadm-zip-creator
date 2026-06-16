import pathlib
from typing import Any
from enum import StrEnum, auto

import flet as ft
import yaml
from sharkadm import utils

from sharkadm_zip_creator.flet_app import event, app_state

USER_DIR = utils.get_root_directory() / 'zip_archive_creator'
USER_DIR.mkdir(parents=True, exist_ok=True)



class Environment(StrEnum):
    TEST = auto()
    PROD = auto()


class UserSavesKeys(StrEnum):
    ZIP_TARGET_DIRECTORY = auto()
    LATEST_SINGLE_DATA_SOURCE = auto()
    LATEST_MULTIPLE_DATA_SOURCE_ROOT = auto()


class ConfigSaves:
    def __init__(self):
        self._env: Environment = Environment.TEST
        self._controls: dict[str, ft.Control] = {}

    def set_env(self, env: str) -> None:
        if Environment(env) not in Environment:
            raise KeyError(env)
        self._env = Environment(env)

    @property
    def present_envs(self) -> list[str]:
        present = []
        for env in Environment:
            if pathlib.Path(USER_DIR, f'zip_archive_creator_saves_{env}.yaml').exists():
                present.append(env)
        return present

    @property
    def save_path(self) -> pathlib.Path:
        return pathlib.Path(USER_DIR, f'zip_archive_creator_saves_{self._env}.yaml').resolve()

    @property
    def valid_save_paths(self) -> list[pathlib.Path]:
        return [pathlib.Path(USER_DIR, f'zip_archive_creator_saves_{env}.yaml') for env in Environment]

    def add_control(self, name: str, control: ft.Control) -> None:
        self._controls[name] = control

    def export_saves(self) -> None:
        data = {}
        for key, cont in self._controls.items():
            data[key] = cont.value
        with open(self.save_path, 'w') as fid:
            yaml.safe_dump(data, fid)

    def import_saves(self, parent: ft.Control) -> None:
        self._clear_all_fields(parent)
        if not self.save_path.exists():
            return
        with open(self.save_path) as fid:
            data = yaml.safe_load(fid)
        for key, value in data.items():
            if not hasattr(parent, key):
                continue
            attr = getattr(parent, key)
            attr.value = value
            attr.update()

    def _clear_all_fields(self, parent: ft.Control) -> None:
        for key, value in self._controls.items():
            if not hasattr(parent, key):
                continue
            attr = getattr(parent, key)
            attr.value = ''
            attr.update()


class UserSaves:
    def __init__(self):
        self._settings: dict[str, Any] = {}
        self._main_app = None
        # print(f"{self._settings=}")
        self.import_saves()

        event.subscribe(event.Events.CHANGE_STATE, self._on_change_state_or_source_type, prio=10)
        event.subscribe(event.Events.CHANGE_SOURCE_TYPE, self._on_change_state_or_source_type, prio=10)

        print("-" * 100)
        print("-" * 100)
        print(f"{list(event.Events)=}")
        print(f"{event._subscribers.keys()=}")
        print(f"{event.__file__=}")
        print(f"{id(event._subscribers)=}")
        print("-" * 100)
        print("-" * 100)

    def set_main_app(self, main_app) -> None:
        self._main_app = main_app
        # print(f"{self._main_app=}")

    def _on_change_state_or_source_type(self, data: dict) -> None:
        pass
        # self.import_saves()

    @property
    def save_path(self) -> pathlib.Path:
        return pathlib.Path(USER_DIR, f'user_saves.yaml').resolve()

    def add_settings(self, **kwargs) -> None:
        # print()
        # print(f"add_settings: {self._settings=}")
        self._settings.update(kwargs)

    def export_saves(self) -> None:
        # print(f"SAVING: {self._settings=} to {self.save_path=}")
        with open(self.save_path, 'w') as fid:
            yaml.safe_dump(self._settings, fid)

    def import_saves(self) -> None:
        # print(f"{self.save_path=}")
        if not self.save_path.exists():
            return
        with open(self.save_path) as fid:
            self._settings = yaml.safe_load(fid)

    def set(self, key: UserSavesKeys, value: Any) -> None:
        if isinstance(value, pathlib.Path):
            value = str(value)
        self._settings[str(key)] = value
        self.export_saves()

    def get(self, key: str, default: Any = None) -> None:
        # print()
        # print("get")
        # print(f"{key=}: {default=}")
        # print
        return self._settings.get(key, default)


config_saves = ConfigSaves()
user_saves = UserSaves()

