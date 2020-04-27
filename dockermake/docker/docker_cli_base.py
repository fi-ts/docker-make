from abc import ABCMeta, abstractmethod


class DockerCliBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def build(self, path, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def docker_cli_version(self):
        raise NotImplementedError

    @abstractmethod
    def inspect(self, name, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def images(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def login(self, server, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def pull(self, image, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def push(self, image, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def remove_images(self, image, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def tag(self, source_image, target_image, **kwargs):
        raise NotImplementedError
