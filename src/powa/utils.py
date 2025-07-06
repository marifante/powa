import yaml
from typing import Any


def parse_yaml_file(file_path) -> Any:
    """ Load the information of a yaml file.

    :param file_path: the path to the yaml file.
    :return: the content of the yaml file.
    """
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
