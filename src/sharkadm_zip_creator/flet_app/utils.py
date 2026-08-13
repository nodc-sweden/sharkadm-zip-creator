import pathlib

import flet as ft
from screeninfo import get_monitors
from sharkadm import utils

USER_DIR = utils.get_root_directory() / "zip_archive_creator"
USER_DIR.mkdir(parents=True, exist_ok=True)
SAVES_PATH = pathlib.Path(USER_DIR, "zip_archive_creator_saves.yaml").resolve()
# CUSTOM_SAVES_PATH = pathlib.Path(USER_DIR, 'custom_saves.yaml').resolve()


def fix_url_str(url: str) -> str:
    prefix = "https://"
    url = url.strip().replace("\\", "/").strip("/")
    if not url:
        return ""
    if not url.startswith(prefix):
        url = prefix + url
    return url


def get_current_monitor(page: ft.Page) -> dict:
    # Fönstrets position
    x = page.window.left
    y = page.window.top
    w = page.window.width
    h = page.window.height

    # Använd fönstrets mittpunkt
    cx = x + w / 2
    cy = y + h / 2

    info = dict()
    info["x"] = x
    info["y"] = y
    info["width"] = w

    for i, m in enumerate(get_monitors()):
        if m.x <= cx < m.x + m.width and m.y <= cy < m.y + m.height:
            print(f"Fönstret är på skärm {i}: {m.width}x{m.height}")
            info["monitor_width"] = m.width
            info["monitor_height"] = m.height
            info["monitor_index"] = i
            info["monitor_name"] = m.name
            info["monitor_is_primary"] = m.is_primary
            return info

    return info
