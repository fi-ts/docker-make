from dockermake.constants import Constants
from dockermake.config.formats.config_1_0 import Config10


class ConfigFactory:
    @staticmethod
    def create_by_version(version, config, cli_args=None):
        if str(version) == "1":
            return Config10(config, cli_args)
        raise Exception("%s in format version %s is not supported" % (Constants.DOCKER_MAKE_YAML, version))
