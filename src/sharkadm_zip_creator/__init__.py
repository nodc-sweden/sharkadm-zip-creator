from nodc_config import Config

from sharkadm_zip_creator.flet_app.app import ZipArchiveCreatorGUI


def run_app(nodc_conf: Config):
    app = ZipArchiveCreatorGUI(nodc_conf)
    return app
