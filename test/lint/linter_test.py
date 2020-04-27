import os
import unittest

from dockermake.dockerfile.dockerfile import Dockerfile
from dockermake.lint.linter import DockerfileLint

from test.helpers import captured_output
from test.helpers import get_mock_dir


class TestDockerfileLint(unittest.TestCase):
    def test_lint_complex_dockerfile(self):
        dockerfile_path = os.path.join(get_mock_dir(), "Dockerfile.complete")
        dockerfile = Dockerfile.load_from_file_path(dockerfile_path)
        linter = DockerfileLint(dockerfile, exit_on_errors=False)

        with captured_output() as (out, err):
            linter.lint()
        output = out.getvalue().strip()

        self.assertIn("---> FAILED", output)
