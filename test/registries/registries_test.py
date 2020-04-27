import copy
import unittest

from mock import patch

from dockermake.registries.registries import Registries


class RegistriesTest(unittest.TestCase):
    def setUp(self):
        self.registries = Registries()
        self.registries.registries = {
            'registry.a': {
                'repositories': [
                    'git.registry-a.de/project-a',
                    'git.registry-a.de/project-b',
                ],
                'auth': {
                    'user': 'user-a',
                    'password': 'password-a'
                }
            },
            'registry.b': {
                'repositories': [
                    'git.registry-b.de/project-a'
                ]
            }
        }

    def test_retrieving_credentials_from_auth_field(self):
        user, password = self.registries.get_registry_authentication("registry.a")

        self.assertEqual(user, 'user-a')
        self.assertEqual(password, 'password-a')

    def test_retrieving_credentials_no_credentials(self):
        user, password = self.registries.get_registry_authentication("registry.b")

        self.assertEqual(user, None)
        self.assertEqual(password, None)

    @patch('dockermake.constants.Constants.REGISTRY_LOGIN_USER', "user-b")
    @patch('dockermake.constants.Constants.REGISTRY_LOGIN_PASSWORD', "password-b")
    def test_retrieving_credentials_from_environment(self):
        user, password = self.registries.get_registry_authentication("registry.b")

        self.assertEqual(user, 'user-b')
        self.assertEqual(password, 'password-b')

    @patch('dockermake.constants.Constants.REGISTRY_LOGIN_USER', "user-b")
    @patch('dockermake.constants.Constants.REGISTRY_LOGIN_PASSWORD', "password-b")
    def test_retrieving_credentials_from_environment_precedence(self):
        user, password = self.registries.get_registry_authentication("registry.a")

        self.assertEqual(user, 'user-a')
        self.assertEqual(password, 'password-a')

    def test_check_allowed_to_push_registry_in_config(self):
        self.registries.push_only_to_defined_registries = True
        self.registries.push_only_to_specific_projects = False
        try:
            self.registries.check_allowed_to_push("registry.a")
        except Exception as exception:
            self.fail("Expected to be able to push to registry.a: %s" % exception)
        with self.assertRaisesRegexp(Exception, "Not allowed to push to docker.io: not defined in registries.yaml"):
            self.registries.check_allowed_to_push("docker.io")

    def test_check_allowed_to_push_without_special_config(self):
        self.registries.push_only_to_defined_registries = False
        self.registries.push_only_to_specific_projects = False
        try:
            self.registries.check_allowed_to_push("docker.io")
        except Exception:
            self.fail("Expected not to fail when trying to push to registry")

    def test_check_allowed_to_push_git_project_only(self):
        self.registries.push_only_to_specific_projects = True
        self.registries.push_only_to_defined_registries = False
        with self.assertRaisesRegexp(Exception, "Not allowed to push to docker.io: not defined in registries.yaml"):
            self.registries.check_allowed_to_push("docker.io")
        with self.assertRaisesRegexp(Exception, "Not allowed to push to registry\.a: Repository .* "
                                                "not defined in registries\.yaml"):
            self.registries.check_allowed_to_push("registry.a")
