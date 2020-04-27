import logging

from dockermake.constants import Constants
from dockermake.utils.helpers import System


def get_docker_version():
    cmd = " ".join([Constants.DOCKER_PATH, "version", "--format", "{{.Server.Version}}"])
    version, _, return_code = System.run_command(cmd, fail_on_bad_return_code=False, shell=True)
    if return_code != 0:
        raise Exception("docker needs to be installed in order to use docker-make")
    suffix = None
    if "+" in version:
        split = version.split("+", 1)
        version = split[0]
    if "-" in version:
        split = version.split("-", 1)
        version = split[0]
        suffix = split[1]
    logging.debug("Found docker version: %s (edition: %s)", version, suffix)
    return version, suffix
