import os

import yaml


def load_config(path):
    """
    Load config from model
    :param path: model path
    :return:
    """
    if os.path.isfile(os.path.join(path, "config.yaml")):
        with open(os.path.join(path, "config.yaml"), "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    else:
        return {}
