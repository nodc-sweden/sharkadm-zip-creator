from collections.abc import Callable

import flet as ft
from flet_app.language import get_text
from sharkadm.sharkadm_logger import adm_logger

LOG_LEVELS = [
    adm_logger.DEBUG,
    adm_logger.INFO,
    adm_logger.WARNING,
    adm_logger.ERROR,
    adm_logger.CRITICAL,
]


@ft.control
class LogLevelSelector(ft.Row):
    on_change: Callable = None
    title: str = get_text("select_log_levels")

    def init(self):
        controls = []
        self._levels = {}
        for level in LOG_LEVELS:
            self._levels[level] = ft.Checkbox(
                label=str(level).upper(),
                on_change=self._on_change,
            )
            controls.append(self._levels[level])
        self._levels[adm_logger.WARNING].value = True
        self._levels[adm_logger.ERROR].value = True
        self._levels[adm_logger.CRITICAL].value = True
        self.controls.append(ft.Text(self.title))
        self.controls.append(ft.Row(controls))

    @property
    def levels(self) -> list[str]:
        return [level for level, wid in self._levels.items() if wid.value]

    def _on_change(self, e: ft.Event[ft.Checkbox]) -> None:
        if self.on_change:
            self.on_change(self.levels)
