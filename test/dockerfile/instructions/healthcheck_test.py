from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class HealthcheckTest(InstructionTest):
    def test_without_options(self):
        instruction = Healthcheck('CMD echo "something"')

        expected = dict(
            interval="30s",
            timeout="30s",
            start_period="0s",
            retries="3",
            cmd='echo "something"'
        )
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_options_and_cmd(self):
        instruction = Healthcheck('--interval=60s --retries=300 CMD cat /proc/process | grep 42')

        expected = dict(
            interval="60s",
            timeout="30s",
            start_period="0s",
            retries="300",
            cmd="cat /proc/process | grep 42"
        )
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_options_and_none(self):
        instruction = Healthcheck('--start-period=5m NONE')

        expected = dict(
            interval="30s",
            timeout="30s",
            start_period="5m",
            retries="3",
            cmd=None
        )
        self.typical_positive_instruction_assertions(instruction, expected)
