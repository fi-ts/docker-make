import unittest

from dockermake.config.formats.config_1_0 import Config10


class Config10Test(unittest.TestCase):
    def test_add_default_build_arg(self):
        config = {}
        config_wrapper = Config10(config)

        config_wrapper._add_default_build_arg("A=42")

        config = config_wrapper.get_config()
        self.assertIn("default-build-args", config)
        default_build_args = config["default-build-args"]
        self.assertEqual(len(default_build_args), 1)
        self.assertEqual(default_build_args[0], "A=42")

    def test_expand(self):
        config = {
            "version": "1",
            "name": "a-name",
            "username": "${NON_EXISTENT:-Klaus}",
            "registry-host": "a-registry-${NAME}",
            "default-build-args": [
                "NAME=test",
                "TAG=default_tag"
            ],
            "builds": [
                {"name": "a-build", "tags": ["${TAG}", "2"]},
                {"name": "b-build", "build-args": ["TAG=build_tag"], "tags": ["${TAG}", "3"]}
            ]
        }
        config_wrapper = Config10(config)

        config_wrapper.expand()

        expected_config = {
            "version": "1",
            "name": "a-name",
            "username": "Klaus",
            "registry-host": "a-registry-test",
            "default-build-args": [
                "NAME=test",
                "TAG=default_tag"
            ],
            "builds": [
                {"name": "a-build", "tags": ["default_tag", "2"]},
                {"name": "b-build", "build-args": ["TAG=build_tag"], "tags": ["build_tag", "3"]}
            ]
        }
        self.assertEqual(config_wrapper.get_config(), expected_config)

    def test_get_default_build(self):
        config = {
            "default-build-name": "b-build",
            "builds": [
                {"name": "a-build"},
                {"name": "b-build"}
            ]
        }
        config_wrapper = Config10(config)

        default_build = config_wrapper.get_default_build()

        self.assertEqual(default_build["name"], "b-build")

    def test_get_default_build_build_not_present(self):
        config = {
            "default-build-name": "a-build",
            "builds": [
                {"name": "b-build"},
                {"name": "c-build"}
            ]
        }
        config_wrapper = Config10(config)

        default_build = config_wrapper.get_default_build()

        self.assertEqual(default_build, None)

    def test_get_image_name(self):
        config = {
            "name": "a-name",
            "username": "a-user",
            "registry-host": "a-registry"
        }
        config_wrapper = Config10(config)

        image_name = config_wrapper.get_image_name()

        self.assertEqual(image_name, "a-registry/a-user/a-name")

    def test_get_image_name_without_registry(self):
        config = {
            "name": "a-name",
            "username": "a-user",
        }
        config_wrapper = Config10(config)

        image_name = config_wrapper.get_image_name()

        self.assertEqual(image_name, "a-user/a-name")

    def test_get_image_name_with_tag(self):
        config = {
            "name": "a-name"
        }
        config_wrapper = Config10(config)

        image_name = config_wrapper.get_image_name(tag="latest")

        self.assertEqual(image_name, "a-name:latest")

    def test_get_before_commands(self):
        config = {
            "before": [
                "first command",
                "second command"
            ]
        }
        config_wrapper = Config10(config)

        commands = config_wrapper.get_before_commands()

        self.assertTrue(isinstance(commands, list))
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0], "first command")
        self.assertEqual(commands[1], "second command")

    def test_get_before_commands_none(self):
        config = {
            "before": None
        }
        config_wrapper = Config10(config)

        commands = config_wrapper.get_before_commands()

        self.assertTrue(isinstance(commands, list))
        self.assertEqual(len(commands), 0)

    def test_get_before_commands_single_command(self):
        config = {
            "before": "first command"
        }
        config_wrapper = Config10(config)

        commands = config_wrapper.get_before_commands()

        self.assertTrue(isinstance(commands, list))
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0], "first command")

    def test_get_build_tags(self):
        config = dict()
        build = {"tags": [1, 1.1, "1.1-dev"]}

        config_wrapper = Config10(config)

        build_tags = config_wrapper.get_build_tags(build)

        self.assertTrue(isinstance(build_tags, list))
        self.assertEqual(len(build_tags), 3)
        self.assertEqual(build_tags[0], "1")
        self.assertEqual(build_tags[1], "1.1")
        self.assertEqual(build_tags[2], "1.1-dev")

    def test_get_build_tags_without_tags(self):
        config = dict()
        build = dict()

        config_wrapper = Config10(config)

        build_tags = config_wrapper.get_build_tags(build)

        self.assertTrue(isinstance(build_tags, list))
        self.assertEqual(len(build_tags), 0)

    def test_get_merged_build_args(self):
        build = {"build-args": ["C=44", "D=45", "E=46"]}
        config = {
            "default-build-args": ["A=42", "B=43", "C=overriden"],
            "builds": [
                build
            ]
        }
        cli_args = ["E=overriden", "F=47"]

        config_wrapper = Config10(config, cli_args)

        build_args = config_wrapper.get_merged_build_args(build)

        self.assertTrue(isinstance(build_args, list))
        self.assertEqual(len(build_args), 6)
        self.assertIn("A=42", build_args)
        self.assertIn("B=43", build_args)
        self.assertIn("C=44", build_args)
        self.assertIn("D=45", build_args)
        self.assertIn("E=46", build_args)
        self.assertIn("F=47", build_args)

    def test_get_merged_build_labels(self):
        build = {"labels": ["1", "2"]}
        config = {
            "default-labels": ["1", "3"],
            "builds": [
                build
            ]
        }

        config_wrapper = Config10(config)

        build_labels = config_wrapper.get_merged_build_labels(build)

        self.assertTrue(isinstance(build_labels, list))
        self.assertEqual(len(build_labels), 3)
        self.assertIn("1", build_labels)
        self.assertIn("2", build_labels)
        self.assertIn("3", build_labels)

    def test_narrow_down_builds_by_names(self):
        config = {
            "builds": [
                {"name": "a-build"},
                {"name": "b-build"}
            ]
        }
        config_wrapper = Config10(config)

        config_wrapper.narrow_down_builds_by_names(["b-build"])

        builds = config_wrapper.get_builds()

        self.assertTrue(isinstance(builds, list))
        self.assertEqual(len(builds), 1)
        self.assertEqual(builds[0]["name"], "a-build")

    def test_narrow_down_builds_by_names_build_name_not_exist(self):
        config = {
            "builds": [
                {"name": "a-build"},
                {"name": "b-build"}
            ]
        }
        config_wrapper = Config10(config)

        with self.assertRaisesRegexp(Exception, "Only-build-name not found in config: c-build"):
            config_wrapper.narrow_down_builds_by_names(["c-build"])

    def test_narrow_down_builds_by_names_no_builds(self):
        config = {"builds": []}
        config_wrapper = Config10(config)

        config_wrapper.narrow_down_builds_by_names([])
