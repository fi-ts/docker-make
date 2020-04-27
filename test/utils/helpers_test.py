import unittest

from dockermake.utils.helpers import System
from test.helpers import captured_output


class SystemTest(unittest.TestCase):
    def test_run_command_with_rc_0(self):
        out, err, rc = System.run_command(["echo", "-n", "42"])
        self.assertEqual(out, "42")
        self.assertEqual(err, "")
        self.assertEqual(rc, 0)

    def test_run_command_with_rc_1(self):
        out, err, rc = System.run_command(["false"], fail_on_bad_return_code=False)
        self.assertEqual(out, "")
        self.assertEqual(err, "")
        self.assertEqual(rc, 1)

    def test_run_command_raises_exception(self):
        try:
            _, _, _ = System.run_command(["false"])
            self.fail()
        except Exception as e:
            self.assertEqual(str(e), "Command returned with exit code 1: false")

    def test_run_command_dry(self):
        with captured_output() as (console_out, console_err):
            out, err, rc = System.run_command("false", dry_run=True)
        self.assertIn("[DRY] Would execute command: false", console_out.getvalue().strip())
        self.assertEqual(out, "")
        self.assertEqual(err, "")
        self.assertEqual(rc, 0)

    def test_run_command_with_continuous_output(self):
        with captured_output():
            out, err, rc = System.run_command(["echo", "-n", "42"], with_continuous_output=True)
        self.assertEqual(out, "42")
        self.assertEqual(err, "")
        self.assertEqual(rc, 0)

    def test_run_command_with_continuous_output_through_shell(self):
        with captured_output():
            out, err, rc = System.run_command(["echo -n 42"], with_continuous_output=True, shell=True)
        self.assertEqual(out, "42")
        self.assertEqual(err, "")
        self.assertEqual(rc, 0)
