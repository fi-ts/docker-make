import os
import unittest

from mock import patch

from dockermake.docker.docker_cli_1_12 import DockerCli112
from test.helpers import get_mock_dir
from test.helpers import mock_registries
from test.helpers import captured_output

from dockermake.dockerfile.dockerfile import Dockerfile
from dockermake.make import Make
from dockermake.cli import parse as parse_arguments
from dockermake.config.config_factory import ConfigFactory
from dockermake.utils.yaml_loader import YamlLoader


class TestMake(unittest.TestCase):
    def test_run_with_dry(self):
        args = ["--dry-run", "--no-lint", "-w", get_mock_dir()]
        make = self.create_make(args=args)

        with captured_output() as (out, err):
            make.run()
        output = out.getvalue().strip()

        self.assertIn("[DRY] Would execute command: docker build", output)
        self.assertIn("[DRY] Would execute command: docker push", output)
        self.assertNotIn("Markdown Summary", output)
        self.assertNotIn("Step", output)

    def test_create_docker_build_and_push_commands_without_buildargs(self):
        config = {
            'name': "a-image-name",
            'username': "a-namespace",
            'registry-host': "registry.a.com",
            'default-build-name': "a-build",
            'default-build-args': [],
            'builds': [{'name': "a-build"}]
        }
        make = self.create_make(args=["--no-pull"], dockerfile="Dockerfile.noargs", config=config)

        with patch("dockermake.utils.helpers.System._run_command", return_value=("", "", 0)) as mock:
            make._run_docker_build_and_push_commands(make.config.get_builds()[0])

        mock.assert_called()

        expected_build_command = (
            "docker build "
            '--label ci.built_from_scratch=true '
            '--file ./Dockerfile '
            '--rm '
            '--tag registry.a.com/a-namespace/a-image-name '
            '.'
        )

        self.assertEqual(" ".join(mock.call_args_list[-3][0][0]), expected_build_command)
        self.assertEqual(" ".join(mock.call_args_list[-2][0][0]),
                          "docker push registry.a.com/a-namespace/a-image-name")
        self.assertEqual(" ".join(mock.call_args_list[-1][0][0]),
                          "docker inspect --format {{ json . }} registry.a.com/a-namespace/a-image-name")

    def test_create_docker_build_and_push_commands_with_buildargs(self):
        builds = [{'name': "a-build", 'build-args': ['A=1', 'B=2']}]
        config = {
            'name': "a-image-name",
            'username': "a-namespace",
            'registry-host': "registry.a.com",
            'default-build-name': "a-build",
            'default-build-args': ['C=3', 'D=4'],
            'builds': builds
        }
        make = self.create_make(args=["--no-pull"], dockerfile="Dockerfile.noargs", config=config)

        with patch("dockermake.utils.helpers.System._run_command", return_value=("", "", 0)) as mock:
            make._run_docker_build_and_push_commands(make.config.get_builds()[0])

        mock.assert_called()

        expected_build_command = (
            "docker build "
            '--build-arg C=3 --build-arg D=4 --build-arg A=1 --build-arg B=2 '
            '--label ci.built_from_scratch=true '
            '--file ./Dockerfile '
            '--rm '
            '--tag registry.a.com/a-namespace/a-image-name '
            '.'
        )
        self.assertEqual(" ".join(mock.call_args_list[-3][0][0]), expected_build_command)
        self.assertEqual(" ".join(mock.call_args_list[-2][0][0]),
                          "docker push registry.a.com/a-namespace/a-image-name")
        self.assertEqual(" ".join(mock.call_args_list[-1][0][0]),
                          "docker inspect --format {{ json . }} registry.a.com/a-namespace/a-image-name")

    def test_create_docker_build_and_push_commands_with_overrides(self):
        config_file = os.path.join(get_mock_dir(), "docker-make-test.yaml")
        config = YamlLoader.safe_load_yaml(config_file)
        make = self.create_make(args=["--no-pull", "--build-arg", "FIRST_VERSION=0.1", "--label", "testlabel"],
                                dockerfile="Dockerfile.noargs", config=config)
        build = make.config.get_builds()[0]

        with patch("dockermake.utils.helpers.System._run_command", return_value=("", "", 0)) as mock:
            make._run_docker_build_and_push_commands(build)

        expected_build_command = (
            "docker build "
            '--build-arg DEFAULT_VERSION=1.0 --build-arg VERSION=overridden --build-arg FIRST_VERSION=0.1 '
            '--label testlabel '
            '--label ci.built_from_scratch=true '
            '--file ./Dockerfile '
            '--rm '
            '--tag registry.a.com/a-namespace/a-image-name '
            '--tag registry.a.com/a-namespace/a-image-name:latest '
            '--tag registry.a.com/a-namespace/a-image-name:0.1 '
            '--tag registry.a.com/a-namespace/a-image-name:overridden '
            '--tag registry.a.com/a-namespace/a-image-name:1.1 '
            '--tag registry.a.com/a-namespace/a-image-name:1.0 '
            '.'
        )
        self.assertEqual(" ".join(mock.call_args_list[-8][0][0]), expected_build_command)
        self.assertEqual(" ".join(mock.call_args_list[-7][0][0]),
                          "docker push registry.a.com/a-namespace/a-image-name")
        self.assertEqual(" ".join(mock.call_args_list[-6][0][0]),
                          "docker push registry.a.com/a-namespace/a-image-name:latest")
        self.assertEqual(" ".join(mock.call_args_list[-5][0][0]),
                          "docker push registry.a.com/a-namespace/a-image-name:0.1")
        self.assertEqual(" ".join(mock.call_args_list[-4][0][0]),
                          "docker push registry.a.com/a-namespace/a-image-name:overridden")
        self.assertEqual(" ".join(mock.call_args_list[-3][0][0]),
                          "docker push registry.a.com/a-namespace/a-image-name:1.1")
        self.assertEqual(" ".join(mock.call_args_list[-2][0][0]),
                          "docker push registry.a.com/a-namespace/a-image-name:1.0")
        self.assertEqual(" ".join(mock.call_args_list[-1][0][0]),
                          "docker inspect --format {{ json . }} registry.a.com/a-namespace/a-image-name")

    @patch.dict(os.environ, dict(TAG_SUFFIX="-dev", ANSIBLE_TOKEN="acme"))
    def test_create_docker_build_and_push_commands_with_two_builds_including_buildargs_and_tags(self):
        config_file = os.path.join(get_mock_dir(), "docker-make-test2.yaml")
        config = YamlLoader.safe_load_yaml(config_file)
        make = self.create_make(
            args=["--no-push", "--build-arg", "ansible_components_version=1.3", "--build-arg", "USERNAME=acme"],
            dockerfile="Dockerfile.args", config=config
        )
        builds = make.config.get_builds()

        self.assertEqual(len(builds), 2)

        with patch("dockermake.utils.helpers.System._run_command", return_value=("", "", 0)) as mock:
            make._run_docker_build_and_push_commands(builds[0])
        expected_build_command = (
            'docker build '
            '--build-arg ansible_components_version=1.3 --build-arg USERNAME=acme '
            '--build-arg ANSIBLE_VERSION=2.4.0.0 --build-arg BOTO_VERSION=2.47 '
            '--build-arg WINRM_VERSION=0.2.2 --build-arg KERBEROS_VERSION=1.2.5 '
            '--build-arg JINJA2_VERSION=2.8.1 --build-arg ANSIBLE_TOKEN=2.4.0.0 '
            '--label ci.built_from_scratch=false '
            '--file ./Dockerfile '
            '--pull '
            '--rm '
            '--tag registry.b.acme/acme/ansible:2.4.0-1.3-dev '
            '--tag registry.b.acme/acme/ansible:2.4.0-dev '
            '--tag registry.b.acme/acme/ansible:2.4-dev '
            '.'
        )

        self.assertEqual(" ".join(mock.call_args_list[-1][0][0]), expected_build_command)

        build_args = builds[0]['build-args']
        self.assertEqual(len(build_args), 6)
        self.assertEqual(build_args[0], "ANSIBLE_VERSION=2.4.0.0")
        self.assertEqual(build_args[1], "BOTO_VERSION=2.47")
        self.assertEqual(build_args[2], "WINRM_VERSION=0.2.2")
        self.assertEqual(build_args[3], "KERBEROS_VERSION=1.2.5")
        self.assertEqual(build_args[4], "JINJA2_VERSION=2.8.1")
        self.assertEqual(build_args[5], "ANSIBLE_TOKEN=2.4.0.0")

        make.args.no_push = False
        with patch("dockermake.utils.helpers.System._run_command", return_value=("", "", 0)) as mock:
            make._run_docker_build_and_push_commands(builds[1])
        expected_build_command = (
            'docker build '
            '--build-arg ansible_components_version=1.3 --build-arg USERNAME=acme '
            '--build-arg ANSIBLE_VERSION=2.3.2.0 --build-arg BOTO_VERSION=2.47 '
            '--build-arg WINRM_VERSION=0.2.2 --build-arg KERBEROS_VERSION=1.2.5 '
            '--build-arg JINJA2_VERSION=2.8.1 --build-arg ANSIBLE_TOKEN=2.3.2.0 '
            '--label ci.built_from_scratch=false '
            '--file ./Dockerfile '
            '--pull '
            '--rm '
            '--tag registry.b.acme/acme/ansible:2.3.2-1.3-dev '
            '--tag registry.b.acme/acme/ansible:2.3.2-dev '
            '--tag registry.b.acme/acme/ansible:2.3-dev '
            '.'
        )
        self.assertEqual(" ".join(mock.call_args_list[-5][0][-0]), expected_build_command)
        self.assertEqual(" ".join(mock.call_args_list[-4][0][-0]),
                          "docker push registry.b.acme/acme/ansible:2.3.2-1.3-dev")
        self.assertEqual(" ".join(mock.call_args_list[-3][0][-0]),
                          "docker push registry.b.acme/acme/ansible:2.3.2-dev")
        self.assertEqual(" ".join(mock.call_args_list[-2][0][-0]), "docker push registry.b.acme/acme/ansible:2.3-dev")
        self.assertEqual(" ".join(mock.call_args_list[-1][0][0]),
                          "docker inspect --format {{ json . }} registry.b.acme/acme/ansible:2.3.2-1.3-dev")

        build_args = builds[1]['build-args']
        self.assertEqual(len(build_args), 6)
        self.assertEqual(build_args[0], "ANSIBLE_VERSION=2.3.2.0")
        self.assertEqual(build_args[1], "BOTO_VERSION=2.47")
        self.assertEqual(build_args[2], "WINRM_VERSION=0.2.2")
        self.assertEqual(build_args[3], "KERBEROS_VERSION=1.2.5")
        self.assertEqual(build_args[4], "JINJA2_VERSION=2.8.1")
        self.assertEqual(build_args[5], "ANSIBLE_TOKEN=2.3.2.0")

    @patch("dockermake.constants.Constants.DEFAULT_PUSH_ONLY_TO_DEFINED_REGISTRIES", True)
    def test_create_docker_build_and_push_commands_push_to_forbidden_registry(self):
        config = {
            'name': "a-image-name",
            'username': "a-namespace",
            'registry-host': "a-forbidden-registry",
            'default-build-name': "a-build",
            'default-build-args': [],
            'builds': [{'name': "a-build"}]
        }
        make = self.create_make(args=["--no-pull"], dockerfile="Dockerfile.noargs", config=config)

        with self.assertRaisesRegex(Exception, "Not allowed to push to a-forbidden-registry: not defined "
                                                "in registries.yaml"):
            with patch("dockermake.utils.helpers.System._run_command", return_value=("", "", 0)):
                make._run_docker_build_and_push_commands(make.config.get_builds()[0])

    @patch("dockermake.git.git.extract_git_repository", return_value="registry.a.com/domain-b")
    def test_create_docker_build_and_push_commands_push_to_allowed_registry(self, _):
        config = {
            'name': "a-image-name",
            'username': "a-username",
            'registry-host': "registry.a.com",
            'default-build-name': "a-build",
            'default-build-args': [],
            'builds': [{'name': "a-build"}]
        }
        make = self.create_make(args=["--no-pull", "--no-push"], dockerfile="Dockerfile.noargs", config=config)

        with patch("dockermake.utils.helpers.System._run_command", return_value=("", "", 0)) as mock:
            make._run_docker_build_and_push_commands(make.config.get_builds()[0])
        mock.assert_called()

        cmd = mock.call_args_list[-1][0][0]
        self.assertEqual("docker", cmd[0])
        self.assertEqual("build", cmd[1])

        make.args.no_push = False
        with patch("dockermake.utils.helpers.System._run_command", return_value=("", "", 0)) as mock:
            make._run_docker_build_and_push_commands(make.config.get_builds()[0])
            mock.assert_called()
            cmd = mock.call_args_list[-1][0][0]
            self.assertIn("inspect", cmd[1])
            cmd = mock.call_args_list[-2][0][0]
            self.assertIn("push", cmd[1])
            cmd = mock.call_args_list[-3][0][0]
            self.assertIn("build", cmd[1])

    def test_get_base_image(self):
        config = {
            'name': "a-image-name",
            'username': "a-username",
            'registry-host': "registry.a.com",
            'default-build-name': "a-build",
            'default-build-args': [],
            'builds': [{'name': "a-build", 'build-args': []}, {'name': "a-build", 'build-args': ["release=8"]}]
        }
        make = self.create_make(args=["--no-pull", "--no-push"], dockerfile="Dockerfile.args_before_from", config=config)
        builds = make.config.get_builds()

        base_image = make._get_base_image(builds[0]['build-args'])
        self.assertEqual("centos:7", base_image)

        base_image = make._get_base_image(builds[1]['build-args'])
        self.assertEqual("centos:8", base_image)

    @patch("dockermake.constants.Constants.CI_BUILD_URL", "http://ci-job/1234")
    @patch("dockermake.make.Make.inspect_image", return_value={"ci.parent_build_urls": '["http://ci-job/1233"]'})
    def test_create_parent_label(self, _):
        make = self.create_make()
        labels = make.create_parent_label("something")

        expected = ['ci.parent_build_urls=["http://ci-job/1233", "http://ci-job/1234"]']
        self.assertEqual(labels, expected)

    @patch("dockermake.constants.Constants.CI_BUILD_URL", "http://ci-job/1234")
    @patch("dockermake.make.Make.inspect_image", return_value={"ci.parent_build_urls": "[http://ci-job/1233]"})
    def test_create_parent_label_compatibility(self, _):
        make = self.create_make()
        labels = make.create_parent_label("something")

        expected = ['ci.parent_build_urls=["http://ci-job/1233", "http://ci-job/1234"]']
        self.assertEqual(labels, expected)

    @staticmethod
    def create_make(args=None, dockerfile="Dockerfile", config=None):
        args = args or []
        config = config or {}
        mock_registries()
        _, parsed_args = parse_arguments(args)
        with patch("dockermake.docker.docker_cli_factory.DockerCliFactory.create", return_value=DockerCli112):
            make = Make(parsed_args)
        dockerfile_path = os.path.join(get_mock_dir(), dockerfile)
        make.dockerfile = Dockerfile.load_from_file_path(dockerfile_path)
        make.config = ConfigFactory.create_by_version("1", config, make.args.docker_build_args)
        make._prepare_config()
        return make
