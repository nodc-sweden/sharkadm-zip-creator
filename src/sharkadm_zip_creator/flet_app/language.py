import re

import yaml
from sharkadm.config import sharkadm_config
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


def get_text(key: str) -> str:
    translated = texts.get(key)
    if not translated:
        translated = key.replace("_", " ").capitalize()
    return translated


texts = dict()
texts.update(get_transformer_translations())
texts.update(get_exporter_translations())
if sharkadm_config and sharkadm_config("lang_en"):
    with open(sharkadm_config("lang_en")) as fid:
        try:
            loaded_texts = yaml.safe_load(fid)
            texts.update(loaded_texts)
        except yaml.YAMLError as exc:
            print(exc)
# texts = dict(
#     configuration_file = "Configuration fileeee"
# )
