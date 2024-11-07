from sharkadm import utils
import pathlib
import yaml


USER_DIR = utils.get_root_directory() / 'zip_archive_creator'
USER_DIR.mkdir(parents=True, exist_ok=True)
SAVES_PATH = pathlib.Path(USER_DIR, 'zip_archive_creator_saves.yaml').resolve()
# CUSTOM_SAVES_PATH = pathlib.Path(USER_DIR, 'custom_saves.yaml').resolve()


def fix_url_str(url: str) -> str:
    prefix = 'https://'
    url = url.strip().replace('\\', '/').strip('/')
    if not url:
        return ''
    if not url.startswith(prefix):
        url = prefix + url
    return url


# class CustomSaves:
#
#     def __init__(self):
#         self._file_path = USER_DIR
#         self._data = {}
#         self._load_file()
#
#     def _load_file(self):
#         if not CUSTOM_SAVES_PATH.exists():
#             return
#         with open(CUSTOM_SAVES_PATH) as fid:
#             self._data = yaml.safe_load(fid)
#
#     def _save_file(self):
#         with open(CUSTOM_SAVES_PATH, 'w') as fid:
#             yaml.safe_dump(self._data, fid)
#
#     def add(self, key, value):
#         self._data[key] = value
#         self._save_file()
#
#     def get(self, key):
#         return self._data.get(key)
#
#
# custom_save = CustomSaves()
