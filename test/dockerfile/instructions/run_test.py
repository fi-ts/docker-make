from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class RunTest(InstructionTest):
    def test_with_exec_form(self):
        instruction = Run('["/bin/bash", "-c", "echo hello"]')

        expected = dict(arguments=["/bin/bash", "-c", "echo hello"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_shell_form(self):
        instruction = Run("/bin/bash -c 'source $HOME/.bashrc; echo $HOME'")

        self.assertEqual(len(instruction.syntax_errors), 0)
        expected = dict(arguments=["/bin/bash -c 'source $HOME/.bashrc; echo $HOME'"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_shell_form_and_subsequent_quotes(self):
        instruction = Run('cut -d" " -f2')

        self.assertEqual(len(instruction.syntax_errors), 0)
        expected = dict(arguments=['cut -d" " -f2'])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_exec_form_and_subsequent_quotes(self):
        instruction = Run("""["cut", "-d' '", "-f2"]""")

        self.assertEqual(len(instruction.syntax_errors), 0)
        expected = dict(arguments=["cut", "-d' '", "-f2"])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_shell_form_complex_expression(self):
        argument = ("""ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa && rsaPub=`cat /home/jcf/.ssh/id_rsa.pub |"""
                    """cut -d" " -f2` \ && echo "jcf=$rsaPub,admin" > ${FUSE_HOME}/etc/keys.properties""")
        instruction = Run(argument)

        self.assertEqual(len(instruction.syntax_errors), 0)
        expected = dict(arguments=[argument])
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_with_variables(self):
        instruction = Run("useradd -rm ${USERNAME} && chown -R ${USERNAME} . && curl http://some.tar")

        self.assertEqual(len(instruction.syntax_errors), 0)
        expected = dict(arguments=["useradd -rm ${USERNAME} && chown -R ${USERNAME} . && curl http://some.tar"])
        self.typical_positive_instruction_assertions(instruction, expected)
