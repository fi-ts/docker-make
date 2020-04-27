import os
import time

from dockermake.config.config_base import ConfigBase
from dockermake.config.validators.config_1_0_validator import Config10Validator
from dockermake.config.interpolation import PosixStyleExpander
from dockermake.utils import display

from dockermake.git.git import get_gitsha1_hash_of_head


class Config10(ConfigBase):
    def __init__(self, config, cli_args=None):
        super(Config10, self).__init__(config, cli_args)
        self.meta_build_args = dict(
            DOCKER_MAKE_GIT_SHA1=get_gitsha1_hash_of_head(),
            DOCKER_MAKE_DATE=lambda: time.strftime("%Y-%m-%d-%H:%M:%S")
        )

    def _add_default_build_arg(self, element):
        self._create_if_not_existent("default-build-args", list)
        self.config["default-build-args"].append(element)

    def expand(self):
        self._create_if_not_existent("default-build-args", list)

        initial_replacement_dict = dict(os.environ)
        initial_replacement_dict.update(self.populated_meta_build_args)

        replacement_dict = self._expand_default_build_args(initial_replacement_dict)

        if "builds" in self.config:
            builds = self.config.pop("builds")
            self._expand_entire_config(replacement_dict)
            self._expand_build_sections_and_add_back(builds, replacement_dict)
        else:
            self._expand_entire_config(replacement_dict)

    def _expand_default_build_args(self, replacement_dict):
        for arg in self.config["default-build-args"]:
            arg = PosixStyleExpander.expand(arg, replacement_dict)
            key, value = arg.split("=", 1)
            replacement_dict[key] = value
        return replacement_dict

    def _expand_entire_config(self, replacement_dict):
        self.config = PosixStyleExpander.expand(self.config, replacement_dict)

    def _expand_build_sections_and_add_back(self, builds, replacement_dict):
        self.config["builds"] = []
        build_replacement_dict = None
        for build in builds:
            build_replacement_dict = replacement_dict
            if "build-args" in build:
                for arg in build["build-args"]:
                    arg = PosixStyleExpander.expand(arg, replacement_dict)
                    key, value = arg.split("=", 1)
                    build_replacement_dict[key] = value

            build = PosixStyleExpander.expand(build, build_replacement_dict)
            self.config["builds"].append(build)
        return build_replacement_dict

    def get_default_build(self):
        """return the default build if any from docker-make.yaml, otherwise None"""
        default_build_name = self.config.get("default-build-name", "")
        if default_build_name and "builds" in self.config:
            for build in self.config["builds"]:
                if build["name"].strip() == default_build_name.strip():
                    return build
        return None

    def get_image_name(self, tag=None):
        image_name = ""
        if "registry-host" in self.config:
            image_name = os.path.join(image_name, self.config["registry-host"])
        if "username" in self.config:
            image_name = os.path.join(image_name, self.config["username"])
        if "name" in self.config:
            image_name = os.path.join(image_name, self.config["name"])
        if image_name and tag:
            image_name = image_name + ":" + tag
        return image_name

    def get_before_commands(self):
        return self.listify(self.config["before"]) if "before" in self.config else []

    def get_after_commands(self):
        return self.listify(self.config["after"]) if "after" in self.config else []

    def get_builds(self):
        return self.config["builds"] if "builds" in self.config else []

    def get_build_tags(self, build):
        tags = build["tags"] if "tags" in build else []
        return [str(tag) for tag in tags]

    def get_before_build_commands(self, build):
        return self.listify(build["before"]) if "before" in build else []

    def get_after_build_commands(self, build):
        return self.listify(build["after"]) if "after" in build else []

    def get_merged_build_args(self, build):
        build_args = list()
        if "default-build-args" in self.config:
            build_args += self.config["default-build-args"]
        if "build-args" in build:
            build_args += build["build-args"]
        return self.remove_duplicate_args(build_args)

    def get_merged_build_labels(self, build):
        labels = set()
        if "default-labels" in self.config:
            labels.update(self.config["default-labels"])
        if "labels" in build:
            labels.update(build["labels"])
        return list(labels)

    def merge_cli_args(self, cli_args):
        if "default-build-args" not in self.config:
            self.config["default-build-args"] = list()
        for arg in cli_args:
            self.config["default-build-args"].append(arg)

    def print_builds(self):
        display.info("Available builds:")
        if "builds" in self.config:
            for build in self.config["builds"]:
                ConfigBase._pprint_complex_data(build)

    def narrow_down_builds_by_names(self, build_names):
        # in Python it is not possible to remove a list element during
        # iteration without making a copy first.
        iteration_list = list(self.get_builds())

        for planned_build in iteration_list:
            if planned_build["name"] not in build_names:
                self.config["builds"].remove(planned_build)

        for build_name in build_names:
            found = False
            for planned_build in self.config["builds"]:
                if build_name == planned_build["name"]:
                    found = True
            if not found:
                raise Exception("only-build-name not found in config: %s" % build_name)

    def get_registry_host(self):
        return self.config["registry-host"]

    def validate(self, dockerfile):
        Config10Validator(self).validate(dockerfile)

    def _create_if_not_existent(self, name, kind):
        if name not in self.config:
            self.config[name] = kind()
