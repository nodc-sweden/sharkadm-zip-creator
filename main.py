import sharkadm_zip_creator
from nodc_config import get_nodc_config


if __name__ == "__main__":
    nodc_conf = get_nodc_config()
    sharkadm_zip_creator.run_app(nodc_conf)
