from distutils.version import StrictVersion

from dockermake.docker import get_docker_version
from dockermake.docker.docker_cli_1_12 import DockerCli112


class DockerCliFactory:
    @staticmethod
    def create(docker_version=None):
        if not docker_version:
            docker_version, _ = get_docker_version()

        if StrictVersion("1.12") <= StrictVersion(docker_version):
            return DockerCli112
        raise Exception("Docker version is not supported: %s" % docker_version)
