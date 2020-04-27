import os

from dockermake.constants import Constants
from dockermake.config.config_factory import ConfigFactory
from dockermake.utils.yaml_loader import YamlLoader


class ConfigLoader:
    NO_DOCKER_MAKE_YAML = """No "{0}" found at "{1}".
    Create a "{0}" with this content to get started:

    version: "1"
    name: yourdockerapplication
    username: yourproject
    registry-host: your.registry.com
    default-build-name: Latest Stable
    builds:
      -
        name: Latest Stable
        tags:
          - 1.0
    """

    @classmethod
    def load(cls, working_directory_path, additional_build_args=None, alternative_file=None):
        if alternative_file:
            yaml_path = os.path.join(working_directory_path, alternative_file)
        else:
            yaml_path_without_ext = os.path.join(working_directory_path, Constants.DOCKER_MAKE_BASE_NAME)
            yaml_path = cls._search_file(yaml_path_without_ext, Constants.YAML_ALLOWED_EXTENSIONS)

        if not yaml_path:
            msg = ConfigLoader.NO_DOCKER_MAKE_YAML.format(Constants.DOCKER_MAKE_YAML, working_directory_path)
            raise Exception(msg)

        return cls.load_from_file_path(yaml_path, additional_build_args)

    @staticmethod
    def _search_file(file_path_without_extension, allowed_extensions):
        for allowed_extension in allowed_extensions:
            possible_path = file_path_without_extension + allowed_extension
            if os.path.isfile(possible_path):
                return possible_path
        return None

    @staticmethod
    def load_from_file_path(yaml_path, additional_build_args=None):
        yaml = YamlLoader.safe_load_yaml(yaml_path)
        if "version" not in yaml:
            raise Exception("%s has no format version" % yaml_path)
        return ConfigFactory.create_by_version(yaml["version"], yaml, additional_build_args)
