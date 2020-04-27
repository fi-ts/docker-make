import os
import unittest

from test.helpers import get_mock_dir

from dockermake.utils.yaml_loader import YamlLoader


class YamlLoaderTest(unittest.TestCase):
    def test_load_valid_yaml(self):
        config_file = os.path.join(get_mock_dir(), "docker-make.yaml")
        config = YamlLoader.safe_load_yaml(config_file)

        self.assertEqual(config["version"], "1")

    def test_load_invalid_yaml(self):
        config_file = os.path.join(get_mock_dir(), "Dockerfile")

        with self.assertRaisesRegexp(Exception, "Unable to parse .*Dockerfile.*"):
            YamlLoader.safe_load_yaml(config_file)
