import unittest

from dockermake.config.loader import ConfigLoader

from test.helpers import get_mock_dir


class TestDockerMake(unittest.TestCase):
    def test_load_config(self):
        config = ConfigLoader.load(get_mock_dir())
        self.assertEqual(config.get_registry_host(), 'registry.b.acme')

    def test_load_alternative_config(self):
        config = ConfigLoader.load(get_mock_dir(), alternative_file="docker-make-test.yaml")
        self.assertEqual(config.get_registry_host(), 'registry.a.com')
