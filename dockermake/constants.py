from distutils.util import strtobool
import os


class Constants:
    DEFAULT_CONFIG_FILE_PATHS = ["./config.yaml", "~/.docker-make/config.yaml", "/etc/docker-make/config.yaml"]
    DEFAULT_LOG_FORMAT = "%(levelname)s: %(message)s"
    DEFAULT_LOG_LEVEL = "ERROR"
    DEFAULT_WORK_DIR = "."
    DEFAULT_SHOW_SENSIBLE_CONSOLE_OUTPUT = False
    DEFAULT_DOCKERFILE = "Dockerfile"
    DEFAULT_REGISTRIES_FILE_PATH = "/etc/docker-make/registries.yaml"
    DEFAULT_PUSH_ONLY_TO_DEFINED_REGISTRIES = False
    DEFAULT_PUSH_ONLY_TO_SPECIFIC_GIT_PROJECTS = False
    DEFAULT_CREATE_PARENT_LABEL = False
    DEFAULT_PARENT_LABEL_NAME = "ci.parent_build_urls"
    DEFAULT_BUILT_FROM_SCRATCH_LABEL_NAME = "ci.built_from_scratch"
    DEFAULT_CREATE_GIT_REMOTE_URL_LABEL = True
    DEFAULT_GIT_REMOTE_URL_LABEL_NAME = "git.remote_url"
    DEFAULT_CREATE_GIT_SHA1_LABEL = True
    DEFAULT_GIT_SHA1_LABEL_NAME = "git.sha1"

    DOCKER_PATH = os.getenv("DOCKER_MAKE_DOCKER_PATH", "docker")
    DOCKER_MAKE_BASE_NAME = "docker-make"
    YAML_ALLOWED_EXTENSIONS = ["." + extension.strip() for extension in
                               os.getenv("DOCKER_MAKE_YAML_ALLOWED_EXTENSIONS", "yml, yaml").split(",")]
    DOCKER_MAKE_YAML = DOCKER_MAKE_BASE_NAME + YAML_ALLOWED_EXTENSIONS[0]

    REGISTRY_LOGIN_USER = os.getenv("DOCKER_MAKE_REGISTRY_LOGIN_USER", None)
    REGISTRY_LOGIN_PASSWORD = os.getenv("DOCKER_MAKE_REGISTRY_LOGIN_PASSWORD", None)

    CI_BUILD_URL = None
    if strtobool(os.getenv("GITLAB_CI", "False")):
        # supports Gitlab
        CI_BUILD_URL = os.getenv("CI_JOB_URL")
    else:
        # supports Jenkins
        CI_BUILD_URL = os.getenv("BUILD_URL")
