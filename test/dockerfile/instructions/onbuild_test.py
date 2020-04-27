from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class OnBuildTest(InstructionTest):
    def test_with_cmd(self):
        instruction = OnBuild('CMD echo -e "hello"')

        expected = dict(onbuild='CMD', arguments=['echo -e "hello"'])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_run(self):
        instruction = OnBuild('RUN /usr/local/bin/python-build --dir /app/src')

        expected = dict(onbuild='RUN', arguments=['/usr/local/bin/python-build --dir /app/src'])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_copy(self):
        instruction = OnBuild('COPY a b')

        expected = dict(onbuild='COPY', src=["a"], dest="b")
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_stopsignal(self):
        instruction = OnBuild('STOPSIGNAL SIGKILL')

        expected = dict(onbuild='STOPSIGNAL', stop_signal='SIGKILL')
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_unknown_keyword(self):
        instruction = OnBuild('UNKNOWN command')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'Instruction of type UNKNOWN does not exist.',
            instruction.syntax_errors[0]
        )

    def test_with_onbuild(self):
        instruction = OnBuild('ONBUILD CMD echo')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'ONBUILD instruction with argument "ONBUILD CMD echo" is invalid: Found unwanted token, "ONBUILD"',
            instruction.syntax_errors[0]
        )

    def test_with_from(self):
        instruction = OnBuild('FROM centos:7')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'ONBUILD instruction with argument "FROM centos:7" is invalid: Found unwanted token, "FROM"',
            instruction.syntax_errors[0]
        )

    def test_with_maintainer(self):
        instruction = OnBuild('MAINTAINER foo')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'ONBUILD instruction with argument "MAINTAINER foo" is invalid: Found unwanted token, "MAINTAINER"',
            instruction.syntax_errors[0]
        )

    def test_with_empty(self):
        instruction = OnBuild('')

        self.assertEqual(len(instruction.syntax_errors), 1)
        self.assertIn(
            'ONBUILD instruction with argument "" is invalid: Expected keyword',
            instruction.syntax_errors[0]
        )
