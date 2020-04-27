from abc import ABCMeta, abstractmethod
import json

from dockermake.utils import display


class ConfigBase:
    __metaclass__ = ABCMeta

    def __init__(self, config, cli_args=None):
        self.meta_build_args = dict()
        self.populated_meta_build_args = dict()
        self.config = config
        if cli_args:
            self.merge_cli_args(cli_args)

    @abstractmethod
    def _add_default_build_arg(self, element):
        raise NotImplementedError

    @abstractmethod
    def get_default_build(self):
        raise NotImplementedError

    @abstractmethod
    def get_image_name(self, tag=None):
        raise NotImplementedError

    @abstractmethod
    def get_before_commands(self):
        raise NotImplementedError

    @abstractmethod
    def get_after_commands(self):
        raise NotImplementedError

    @abstractmethod
    def get_builds(self):
        raise NotImplementedError

    @abstractmethod
    def get_build_tags(self, build):
        raise NotImplementedError

    @abstractmethod
    def get_before_build_commands(self, build):
        raise NotImplementedError

    @abstractmethod
    def get_after_build_commands(self, build):
        raise NotImplementedError

    @abstractmethod
    def expand(self):
        raise NotImplementedError

    @abstractmethod
    def merge_cli_args(self, cli_args):
        raise NotImplementedError

    @abstractmethod
    def get_merged_build_args(self, build):
        raise NotImplementedError

    @abstractmethod
    def get_merged_build_labels(self, build):
        raise NotImplementedError

    @abstractmethod
    def narrow_down_builds_by_names(self, build_names):
        raise NotImplementedError

    @abstractmethod
    def get_registry_host(self):
        raise NotImplementedError

    @abstractmethod
    def print_builds(self):
        raise NotImplementedError

    @abstractmethod
    def validate(self, dockerfile):
        raise NotImplementedError

    def add_metadata_to_config(self, dockerfile):
        """
        Add metadata build arguments to the configuration, but only if the argument is mentioned in the Dockerfile.
        """
        for name, arg in self.meta_build_args.items():
            if callable(arg):
                value = arg()
            else:
                value = arg
            if value:
                if dockerfile is not None and dockerfile.contains_arg_with_name(name):
                    self._add_default_build_arg("%s=%s" % (name, value))
                self.populated_meta_build_args.update({name: value})

    def get_config(self):
        return self.config

    @staticmethod
    def _pprint_complex_data(data):
        display.info(json.dumps(data, indent=4, sort_keys=True))

    @staticmethod
    def listify(data):
        if isinstance(data, list):
            return data
        if data is None:
            return []
        return [data]

    @staticmethod
    def remove_duplicate_args(arg_list):
        """The last arg of the duplicates in the list wins"""
        distinct = dict()
        for arg in arg_list:
            key, value = arg.split("=", 1)
            distinct[key] = value

        unique_list = list()
        for key, value in distinct.items():
            unique_list.append(key + "=" + value)
        return unique_list
