import os
import jsonschema

from dockermake.utils.helpers import load_json
from dockermake.dockerfile.instructions import Keywords


class Config10Validator:
    """
    Config must have at least:
        1. a valid yaml schema
        2. one builds section
        3. inside builds a name
        4. all non default-builds must have a tags section with at least one tag
        5. if default-build-name is specified, a matching build.name must be present
        6. names of all builds must be unique
        7. name, username, registry-host must be present
        8. all tags must be unique
        9. all ARGs specified in Dockerfile must be specified by build-args
        10. all build-args must be unique per section
        11. all labels must be unique per section
    """

    JSON_SCHEMA = "schema_1_0.json"

    def __init__(self, config):
        self.config_wrapper = config
        self.config = config.config
        self.errors = list()

    def validate(self, dockerfile):
        self.has_valid_schema()
        self.has_one_builds_section()
        self.builds_have_names()
        self.non_default_builds_have_tags()
        self.default_build_is_defined()
        self.build_names_are_unique()
        self.main_keys_are_present()
        self.all_tags_are_unique()
        self.args_in_dockerfile(dockerfile)
        self.build_args_unique_per_section()
        self.labels_are_unique_per_section()

    def has_valid_schema(self):
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas", self.JSON_SCHEMA)
        schema = load_json(schema_path)
        try:
            jsonschema.validate(self.config, schema)
        except jsonschema.exceptions.ValidationError as exception:
            self.error("The docker-make.yaml schema is invalid: %s" % str(exception))

    def has_one_builds_section(self):
        if 'builds' not in self.config:
            self.error("There must be at least one builds defined")
        else:
            builds = self.config['builds']
            if builds is None:
                self.error("There configured builds must not be None")

    def builds_have_names(self):
        for build in self.config_wrapper.get_builds():
            if 'name' not in build:
                self.error("Build without name found")
            elif build['name'].strip() == '':
                self.error("Build with empty name found")

    def non_default_builds_have_tags(self):
        default_build = self.config_wrapper.get_default_build()
        for build in self.config_wrapper.get_builds():
            if build is default_build:
                continue
            if 'tags' not in build:
                self.error("Non default build must have a tags section")
            else:
                tags = build['tags']
                if not tags:
                    self.error("Non default build must have at least one tag")

    def default_build_is_defined(self):
        default_build = self.config_wrapper.get_default_build()
        if default_build is None and 'default-build-name' in self.config:
            self.error("The default-build-name is not defined in builds")

    def build_names_are_unique(self):
        builds = self.config_wrapper.get_builds()
        names = set()
        for build in builds:
            names.add(build['name'])
        if len(names) < len(builds):
            self.error("Build names are not unique")

    def main_keys_are_present(self):
        if 'name' not in self.config:
            self.error("There must be at least name defined")
        if 'username' not in self.config:
            self.error("There must be at least username defined")
        if 'registry-host' not in self.config:
            self.error("There must be at least registry-host defined")

    def all_tags_are_unique(self):
        tag_names = set()
        tag_count = 0
        for build in self.config_wrapper.get_builds():
            if 'tags' in build:
                tags = build['tags']
                if not isinstance(tags, list):
                    self.error("Tags section must be a list")
                for tag in tags:
                    tag_count += 1
                    tag_names.add(tag)
        if len(tag_names) != tag_count:
            self.error("Tags are not unique")

    def args_in_dockerfile(self, dockerfile):
        args = set(arg_instruction.name for arg_instruction
                   in dockerfile.get_instructions_of_type(Keywords.ARG)
                   if arg_instruction.default is None)
        builds = self.config_wrapper.get_builds()
        if args and not builds:
            self.error("ARG %s in Dockerfile specified but no build section specified" % (", ".join(args)))

        for build in builds:
            args_found = set()
            for arg in args:
                if 'build-args' in build:
                    for build_arg in build['build-args']:
                        if self.matches(arg, build_arg):
                            args_found.add(arg)
                if 'default-build-args' in self.config:
                    for default_build_arg in self.config['default-build-args']:
                        if self.matches(arg, default_build_arg):
                            args_found.add(arg)
            args_not_found = list(args - args_found - set(self.config_wrapper.meta_build_args.keys()))
            if args_not_found:
                build_name = build['name'] if "name" in build else ""
                self.error("ARG %s in Dockerfile specified but not in build-args of build \"%s\"" %
                           (", ".join(args_not_found), build_name))

    def build_args_unique_per_section(self):
        if 'default-build-args' in self.config:
            duplicates = self.has_duplicate_keys(self.config['default-build-args'])
            if duplicates:
                self.error("default-build-args have duplicate keys: %s" % ", ".join(duplicates))
        for build in self.config_wrapper.get_builds():
            if 'build-args' in build:
                duplicates = self.has_duplicate_keys(build['build-args'])
                if duplicates:
                    self.error("build-args of %s have duplicate keys: %s" % (build['name'], ", ".join(duplicates)))

    def labels_are_unique_per_section(self):
        if 'default-labels' in self.config:
            duplicates = self.has_duplicate_keys(self.config['default-labels'])
            if duplicates:
                self.error("default-labels have duplicate keys: %s" % ", ".join(duplicates))
        for build in self.config_wrapper.get_builds():
            if 'labels' in build:
                labels = build['labels']
                if isinstance(labels, dict):
                    self.error("Labels section must contain a list")
                duplicates = self.has_duplicate_keys(labels)
                if duplicates:
                    self.error("labels of %s have duplicate keys: %s" % (build['name'], ", ".join(duplicates)))

    def error(self, msg):
        self.errors.append(msg)

    @staticmethod
    def has_duplicate_keys(build_args):
        """check if build_args has duplicate keys and return them"""
        all_keys = list()
        for build_arg in build_args:
            key = build_arg.split('=')[0].strip()
            all_keys.append(key)
        seen = set()
        dup = list()
        for key in all_keys:
            if key not in seen:
                seen.add(key)
            else:
                dup.append(key)
        return dup

    @staticmethod
    def matches(arg, build_arg):
        """check if arg is equal to build_arg, returns true, otherwise false"""
        build_arg_key = build_arg.split('=')[0].strip()
        return build_arg_key == arg
