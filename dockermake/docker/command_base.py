import inspect
from abc import ABCMeta, abstractmethod
import logging

from dockermake.constants import Constants
from dockermake.utils.helpers import System


class CommandBase:
    __metaclass__ = ABCMeta

    BASE = Constants.DOCKER_PATH

    def __init__(self, **kwargs):
        arg_spec = inspect.getfullargspec(System.run_command)
        default_args = arg_spec.args[-len(arg_spec.defaults):]
        self.command_options = dict()
        for default_arg in default_args:
            if default_arg in kwargs:
                self.command_options[default_arg] = kwargs.pop(default_arg)

        if kwargs:
            self.argument_error(kwargs)

        self.command = self._build_command()

    @abstractmethod
    def _build_command(self):
        raise NotImplementedError

    def get(self):
        return self.command

    def run(self):
        return System.run_command(self.command, **self.command_options)

    @staticmethod
    def argument_error(kwargs):
        logging.error("Docker Command Builder called with unknown args: %s", kwargs)

    @classmethod
    def _base(cls):
        parts = list()
        parts.append(cls.BASE)
        return parts
