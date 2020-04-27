import unittest

from mock import patch
from testfixtures import log_capture

from dockermake.docker.command_base import CommandBase
from dockermake.docker.docker_cli_1_12 import DockerCli112
from test.helpers import is_sublist


class DockerCli112Test(unittest.TestCase):
    def test_build_command(self):
        self.command = DockerCli112.BuildCommand("centos:7")

        self.typical_command_assertions("build", "centos:7")

    def test_build_command_with_all_args(self):
        self.command = DockerCli112.BuildCommand("centos:7", build_args=["arg1", "arg2"], labels=["label1"],
                                                 pull=True, remove=True, tags=["1", "2", "3"], quiet=True)

        self.typical_command_assertions("build",
                                        "centos:7",
                                        ["--build-arg", "arg1"],
                                        ["--build-arg", "arg2"],
                                        ["--label", "label1"],
                                        "--pull",
                                        "--rm",
                                        ["--tag", "1"],
                                        ["--tag", "2"],
                                        ["--tag", "3"],
                                        "--quiet")

    def test_inspect_command(self):
        self.command = DockerCli112.InspectCommand("centos:7")

        self.typical_command_assertions("inspect", "centos:7")

    def test_inspect_command_with_all_args(self):
        self.command = DockerCli112.InspectCommand("alpine:latest", output_format="{{ json }}", size=True)

        self.typical_command_assertions("inspect", "alpine:latest", ["--format", "{{ json }}"], "--size")

    def test_images_command(self):
        self.command = DockerCli112.ImagesCommand()

        self.typical_command_assertions("images")

    def test_images_command_with_all_args(self):
        self.command = DockerCli112.ImagesCommand(image="alpine:latest", all_images=True, digests=True,
                                                  image_filter="some_filter", output_format="{{ json }}",
                                                  no_trunc=True, quiet=True)

        self.typical_command_assertions("images", "alpine:latest", "--all", "--digests",
                                        ["--filter", "some_filter"], ["--format", "{{ json }}"],
                                        "--no-trunc", "--quiet")

    def test_login_command(self):
        self.command = DockerCli112.LoginCommand("registry.com", user="foo", password="bar")

        self.typical_command_assertions("login", "registry.com", ["--username", "foo"], ["--password-stdin"])

    def test_pull_command(self):
        self.command = DockerCli112.PullCommand("centos:7")

        self.typical_command_assertions("pull", "centos:7")

    def test_pull_command_with_all_args(self):
        self.command = DockerCli112.PullCommand("alpine:latest", all_tags=True, disable_content_trust=True)

        self.typical_command_assertions("pull", "alpine:latest", "--all-tags", "--disable-content-trust")

    def test_push_command(self):
        self.command = DockerCli112.PushCommand("my-image:latest")

        self.typical_command_assertions("push", "my-image:latest")

    def test_push_command_with_all_args(self):
        self.command = DockerCli112.PushCommand("my-image:latest", disable_content_trust=True)

        self.typical_command_assertions("push", "my-image:latest", "--disable-content-trust")

    def test_remove_images_command(self):
        self.command = DockerCli112.RemoveImagesCommand("my-image")

        self.typical_command_assertions("rmi", "my-image")

    def test_remove_images_command_with_all_args(self):
        self.command = DockerCli112.RemoveImagesCommand("my-image", force=True, no_prune=True)

        self.typical_command_assertions("rmi", "my-image", "--force", "--no-prune")

    def test_tag_command(self):
        self.command = DockerCli112.TagCommand("ansible:2.4", "ansible:latest")

        self.typical_command_assertions("tag", ["ansible:2.4", "ansible:latest"])

    @log_capture()
    def test_build_command_unknown_arg(self, log):
        self.command = DockerCli112.BuildCommand("alpine:latest", something_unknown=True)

        self.assertLog(log.records[-1], "ERROR", "called with unknown args")
        self.typical_command_assertions("build", "alpine:latest")

    def typical_command_assertions(self, base_command, *args):
        self.command = self.command._build_command()
        self.assertEqual(self.command[0], CommandBase.BASE)
        self.assertEqual(self.command[1], base_command)
        for arg in args:
            if isinstance(arg, list):
                self.assertTrue(is_sublist(self.command, arg), "'%s' sublist not found in '%s'" % (arg, self.command))
            else:
                self.assertIn(arg, self.command)

    def assertLog(self, log_record, level_name=None, *args):
        if level_name:
            self.assertEqual(log_record.levelname, level_name)

        for arg in args:
            self.assertIn(arg.lower(), log_record.getMessage().lower())
