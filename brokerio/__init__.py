import logging
import os

import yaml


def init_logging(name=None, level=logging.DEBUG):
    if name is None:
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(name)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(level)
    return logger


def load_config(config_file=None):
    if config_file is None or config_file == "":
        # load default config
        with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    else:
        if not os.path.exists(config_file):
            raise FileNotFoundError("Config file not found")
        with open(config_file, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
