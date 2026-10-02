import re
import traceback

import yaml
from nodc_config import Config
from sharkadm.exporters import get_exporter_list
from sharkadm.transformers import get_transformer_list


def pascal_to_text(string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", string).capitalize()


def get_transformer_translations() -> dict[str, str]:
    translations = dict()
    for trans in get_transformer_list():
        name = trans
        if trans.startswith("_"):
            continue
        name = name.removeprefix("Polars")
        translations[trans] = pascal_to_text(name)
    return translations


def get_exporter_translations() -> dict[str, str]:
    translations = dict()
    for exp in get_exporter_list():
        name = exp
        if exp.startswith("_"):
            continue
        name = name.removeprefix("Polars")
        name = pascal_to_text(name)
        name = f"Create {name}"
        translations[exp] = name
    return translations


class Language:
    def __init__(self, nodc_conf: Config, lang: str = "en") -> None:
        self._nodc_conf = nodc_conf
        self._lang = lang
        self._texts = dict()
        self.load_config(self._lang)

    @property
    def config_name(self) -> str:
        return f"lang_{self._lang}"

    def load_config(self, lang: str) -> None:
        self._lang = lang
        self._texts.update(get_transformer_translations())
        self._texts.update(get_exporter_translations())
        lang_path = self._nodc_conf(self.config_name)
        if lang_path:
            with open(lang_path) as fid:
                try:
                    loaded_texts = yaml.safe_load(fid)
                    self._texts.update(loaded_texts)
                except yaml.YAMLError:
                    print(traceback.format_exc())

    def get_text(self, key: str) -> str:
        translated = self._texts.get(key)
        if not translated:
            translated = key.replace("_", " ").capitalize()
        return translated


# texts = dict(
#     configuration_file = "Configuration fileeee"
# )
