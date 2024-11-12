import pathlib
from typing import Any

import flet as ft
import yaml
from sharkadm import utils

USER_DIR = utils.get_root_directory() / 'zip_archive_creator'
USER_DIR.mkdir(parents=True, exist_ok=True)


class ConfigSaves:
    def __init__(self):
        self._env: str = 'test'
        self._controls: dict[str, ft.Control] = {}

    def set_env(self, env: str) -> None:
        env = env.strip().upper()
        if env not in self.envs:
            raise KeyError(env)
        self._env = env

    @property
    def envs(self) -> list[str]:
        return ['TEST', 'UTV', 'PROD', 'LOKALT']

    @property
    def present_envs(self) -> list[str]:
        present = []
        for env in self.envs:
            if pathlib.Path(USER_DIR, f'zip_archive_creator_saves_{env}.yaml').exists():
                present.append(env)
        return present

    @property
    def save_path(self) -> pathlib.Path:
        return pathlib.Path(USER_DIR, f'zip_archive_creator_saves_{self._env}.yaml').resolve()

    @property
    def valid_save_paths(self) -> list[pathlib.Path]:
        return [pathlib.Path(USER_DIR, f'zip_archive_creator_saves_{env}.yaml') for env in self.envs]

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

    @property
    def save_path(self) -> pathlib.Path:
        return pathlib.Path(USER_DIR, f'user_saves.yaml').resolve()

    def add_settings(self, **kwargs) -> None:
        self._settings.update(kwargs)

    def export_saves(self) -> None:
        with open(self.save_path, 'w') as fid:
            yaml.safe_dump(self._settings, fid)

    def import_saves(self) -> None:
        if not self.save_path.exists():
            return
        with open(self.save_path) as fid:
            self._settings = yaml.safe_load(fid)

    def get(self, key: str, default: Any = None) -> None:
        return self._settings.get(key, default)


config_saves = ConfigSaves()
user_saves = UserSaves()

