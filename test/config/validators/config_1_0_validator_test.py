import os
import unittest

from dockermake.config.formats.config_1_0 import Config10
from dockermake.config.validators.config_1_0_validator import Config10Validator
from dockermake.dockerfile.dockerfile import Dockerfile
from test.helpers import get_mock_dir


class Config10ValidatorTest(unittest.TestCase):
    def test_has_one_builds_section(self):
        config = {'builds': [{'name': "a-build"}]}
        validator = self.get_validator_from_config(config)

        validator.has_one_builds_section()

        self.assertEqual(len(validator.errors), 0)

    def test_has_one_builds_section_without_build_section(self):
        config = {}
        validator = self.get_validator_from_config(config)

        validator.has_one_builds_section()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], "There must be at least one builds defined")

    def test_has_one_builds_section_with_missing_build(self):
        config = {'builds': None}
        validator = self.get_validator_from_config(config)

        validator.has_one_builds_section()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], "There configured builds must not be None")

    def test_builds_have_names(self):
        config = {'builds': [{'name': "a-build"}, {'name': 'b-build'}]}
        validator = self.get_validator_from_config(config)

        validator.builds_have_names()

        self.assertEqual(len(validator.errors), 0)

    def test_builds_have_names_empty_build(self):
        config = {'builds': [{'name': "a-build"}, {}]}
        validator = self.get_validator_from_config(config)

        validator.builds_have_names()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], "Build without name found")

    def test_builds_have_names_build_without_name(self):
        config = {'builds': [{'name': "a-build"}, {'name': ''}]}
        validator = self.get_validator_from_config(config)

        validator.builds_have_names()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], "Build with empty name found")

    def test_builds_have_names_no_builds_at_all(self):
        config = {}
        validator = self.get_validator_from_config(config)

        validator.builds_have_names()

        self.assertEqual(len(validator.errors), 0)

    def test_non_default_builds_have_tags(self):
        config = {
            'default-build-name': 'a-build',
            'builds': [{'name': "a-build"}, {'name': 'b-build', 'tags': ['1', '2']}]}
        validator = self.get_validator_from_config(config)

        validator.non_default_builds_have_tags()

        self.assertEqual(len(validator.errors), 0)

    def test_non_default_builds_have_tags_missing_tags(self):
        config = {
            'default-build-name': 'a-build',
            'builds': [{'name': "a-build"}, {'name': 'b-build'}]}
        validator = self.get_validator_from_config(config)

        validator.non_default_builds_have_tags()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], "Non default build must have a tags section")

    def test_non_default_builds_have_tags_no_tags(self):
        config = {
            'default-build-name': 'a-build',
            'builds': [{'name': "a-build"}, {'name': 'b-build', 'tags': []}]}
        validator = self.get_validator_from_config(config)

        validator.non_default_builds_have_tags()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], "Non default build must have at least one tag")

    def test_default_build_is_defined(self):
        config = {
            'default-build-name': 'a-build',
            'builds': [{'name': "a-build"}]}
        validator = self.get_validator_from_config(config)

        validator.default_build_is_defined()

        self.assertEqual(len(validator.errors), 0)

    def test_default_build_is_defined_no_match(self):
        config = {
            'default-build-name': 'a-build',
            'builds': [{'name': "b-build"}]}
        validator = self.get_validator_from_config(config)

        validator.default_build_is_defined()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], "The default-build-name is not defined in builds")

    def test_default_build_is_defined_no_builds_at_all(self):
        config = {'default-build-name': 'a-build'}
        validator = self.get_validator_from_config(config)

        validator.default_build_is_defined()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], "The default-build-name is not defined in builds")

    def test_build_names_are_unique_no_builds_section(self):
        config = {}
        validator = self.get_validator_from_config(config)

        validator.build_names_are_unique()

        self.assertEqual(len(validator.errors), 0)

    def test_build_names_are_unique(self):
        config = {'builds': [{'name': "a-build"}, {'name': "b-build"}]}
        validator = self.get_validator_from_config(config)

        validator.build_names_are_unique()

        self.assertEqual(len(validator.errors), 0)

    def test_build_names_are_unique_with_duplicate(self):
        config = {'builds': [{'name': "a-build"}, {'name': "a-build"}]}
        validator = self.get_validator_from_config(config)

        validator.build_names_are_unique()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], "Build names are not unique")

    def test_main_keys_are_present(self):
        config = {
            'name': "a-image-name",
            'username': "a-namespace",
            'registry-host': "registry.a.com",
            'default-build-name': "a-build",
        }
        validator = self.get_validator_from_config(config)

        validator.main_keys_are_present()

        self.assertEqual(len(validator.errors), 0)

    def test_main_keys_are_present_no_values(self):
        config = dict()
        validator = self.get_validator_from_config(config)

        validator.main_keys_are_present()

        self.assertEqual(len(validator.errors), 3)
        self.assertEqual(validator.errors[0], 'There must be at least name defined')
        self.assertEqual(validator.errors[1], 'There must be at least username defined')
        self.assertEqual(validator.errors[2], 'There must be at least registry-host defined')

    def test_main_keys_are_present_only_registry_missing(self):
        config = {
            'name': "a-image-name",
            'username': "a-namespace",
            'default-build-name': "a-build",
            'default-build-args': [],
            'builds': [{'name': "a-build"}]
        }
        validator = self.get_validator_from_config(config)

        validator.main_keys_are_present()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], 'There must be at least registry-host defined')

    def test_all_tags_are_unique_without_builds_section(self):
        config = {}
        validator = self.get_validator_from_config(config)

        validator.all_tags_are_unique()

        self.assertEqual(len(validator.errors), 0)

    def test_all_tags_are_unique(self):
        config = {
            'builds': [
                {'name': "a-build", "tags": ["1.0", "1.1"]},
                {'name': "b-build", "tags": ["1.2"]}
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.all_tags_are_unique()

        self.assertEqual(len(validator.errors), 0)

    def test_all_tags_are_unique_duplicate_in_other_build(self):
        config = {
            'builds': [
                {'name': "a-build", "tags": ["1.0", "1.1"]},
                {'name': "b-build", "tags": ["1.1"]}
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.all_tags_are_unique()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], 'Tags are not unique')

    def test_all_tags_are_unique_duplicate_in_same_build(self):
        config = {
            'builds': [
                {'name': "a-build", "tags": ["1.0", "1.0"]},
                {'name': "b-build", "tags": ["1.1"]}
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.all_tags_are_unique()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], 'Tags are not unique')

    def test_all_tags_are_unique_tags_are_not_a_list(self):
        config = {
            'builds': [
                {'name': "a-build", "tags": "1.0"}
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.all_tags_are_unique()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], 'Tags section must be a list')

    def test_args_in_dockerfile(self):
        dockerfile_path = os.path.join(get_mock_dir(), "Dockerfile.args")
        dockerfile = Dockerfile.load_from_file_path(dockerfile_path)
        config = {
            'builds': [
                {"name": "a-build", "build-args": ["V1=42", "V2=3,14", "V3=9000"]},
                {"name": "b-build", "build-args": ["V1=43", "V2=3,15", "V3=9000"]}
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.args_in_dockerfile(dockerfile)

        self.assertEqual(len(validator.errors), 0)

    def test_args_in_dockerfile_one_arg_missing_in_one_build(self):
        dockerfile_path = os.path.join(get_mock_dir(), "Dockerfile.args")
        dockerfile = Dockerfile.load_from_file_path(dockerfile_path)
        config = {
            'builds': [
                {"name": "a-build", "build-args": ["V1=42", "V2=3,14", "V3=9000"]},
                {"name": "b-build", "build-args": ["V1=43", "V2=3,15"]}
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.args_in_dockerfile(dockerfile)

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0],
                         'ARG V3 in Dockerfile specified but not in build-args of build "b-build"')

    def test_args_in_dockerfile_three_args_missing_in_one_build_and_another_has_no_args(self):
        dockerfile_path = os.path.join(get_mock_dir(), "Dockerfile.args")
        dockerfile = Dockerfile.load_from_file_path(dockerfile_path)
        config = {
            'builds': [
                {"name": "a-build", "build-args": []},
                {"name": "b-build"}
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.args_in_dockerfile(dockerfile)

        self.assertEqual(len(validator.errors), 2)
        self.assertRegex(validator.errors[0],
                         'ARG V[1-3], V[1-3], V[1-3] in Dockerfile specified but not in build-args of build "a-build"')
        self.assertRegex(validator.errors[1],
                         'ARG V[1-3], V[1-3], V[1-3] in Dockerfile specified but not in build-args of build "b-build"')

    def test_args_in_dockerfile_empty_config(self):
        dockerfile_path = os.path.join(get_mock_dir(), "Dockerfile.args")
        dockerfile = Dockerfile.load_from_file_path(dockerfile_path)
        config = {}
        validator = self.get_validator_from_config(config)

        validator.args_in_dockerfile(dockerfile)

        self.assertEqual(len(validator.errors), 1)
        self.assertRegex(validator.errors[0],
                         'ARG V[1-3], V[1-3], V[1-3] in Dockerfile specified but no build section specified')

    def test_build_args_unique_per_section(self):
        config = {
            'default-build-name': 'a-build',
            'default-build-args': ["a=avalue"],
            'builds': [
                {'name': "a-build", "build-args": ["b=bvalue"]}
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.build_args_unique_per_section()

        self.assertEqual(len(validator.errors), 0)

    def test_build_args_unique_per_section_duplicate_in_defaults(self):
        config = {
            'default-build-name': 'a-build',
            'default-build-args': ["a=avalue", "a=anothervalue"],
            'builds': [
                {'name': "a-build", "build-args": ["b=bvalue", "a=anothervalue"]}
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.build_args_unique_per_section()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], 'default-build-args have duplicate keys: a')

    def test_build_args_unique_per_section_duplicate_in_builds(self):
        config = {
            'default-build-name': 'a-build',
            'builds': [
                {'name': "a-build", "build-args": ["a=avalue", "a=anothervalue", "b=bvalue", "b=anothervalue"]}
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.build_args_unique_per_section()

        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0], 'build-args of a-build have duplicate keys: a, b')

    def test_build_args_unique_per_section_empty_config(self):
        config = {}
        validator = self.get_validator_from_config(config)

        validator.build_args_unique_per_section()

        self.assertEqual(len(validator.errors), 0)

    def test_labels_are_unique_per_section(self):
        config = {
            'default-build-name': 'a-build',
            'default-labels': ["1.0"],
            'builds': [
                {'name': "a-build", "labels": ["1.0"]},
                {'name': "a-build", "labels": ["1.0", "1.1"]},
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.labels_are_unique_per_section()

        self.assertEqual(len(validator.errors), 0)

    def test_labels_are_unique_per_section_one_duplicate_in_build_and_default(self):
        config = {
            'default-build-name': 'a-build',
            'default-labels': ["1.0", "1.0"],
            'builds': [
                {'name': "a-build", "labels": ["1.0"]},
                {'name': "a-build", "labels": ["1.1", "1.2", "1.1", "1.2"]},
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.labels_are_unique_per_section()

        self.assertEqual(len(validator.errors), 2)
        self.assertEqual(validator.errors[0], 'default-labels have duplicate keys: 1.0')
        self.assertEqual(validator.errors[1], 'labels of a-build have duplicate keys: 1.1, 1.2')

    def test_has_valid_schema(self):
        config = {
            "version": "1",
            "name": "a-name",
            "username": "a-username",
            "registry-host": "a-registry",
            "builds": [
                {
                    "name": "a-build"
                }
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.has_valid_schema()

        self.assertEqual(len(validator.errors), 0)

    def test_has_valid_schema_unexpected_keyword(self):
        config = {
            "version": "1",
            "name": "a-name",
            "username": "a-username",
            "registry-host": "a-registry",
            "unexpected-keyword": "not-part-of-schema",
            "builds": [
                {
                    "name": "a-build"
                }
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.has_valid_schema()

        self.assertEqual(len(validator.errors), 1)
        self.assertIn(
            "The docker-make.yaml schema is invalid: Additional properties are not allowed ('unexpected-keyword' was unexpected)",
            validator.errors[0])

    def test_has_valid_schema_build_is_not_an_object(self):
        config = {
            "version": "1",
            "name": "a-name",
            "username": "a-username",
            "registry-host": "a-registry",
            "builds": [
                {"name": "42"},
                "something"
            ]
        }
        validator = self.get_validator_from_config(config)

        validator.has_valid_schema()

        self.assertEqual(len(validator.errors), 1)
        self.assertIn("The docker-make.yaml schema is invalid: 'something' is not of type 'object'",
                      validator.errors[0])

    @staticmethod
    def get_validator_from_config(config):
        config_wrapper = Config10(config)
        return Config10Validator(config_wrapper)
