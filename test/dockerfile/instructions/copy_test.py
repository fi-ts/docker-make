from test.instructions import *
from test.dockerfile.instructions import InstructionTest


class CopyTest(InstructionTest):
    def test_copy(self):
        instruction = Copy('source_path_a/something.py /')

        expected = {
            "src": ["source_path_a/something.py"], "dest": "/", "chown": None, "from": None
        }
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_copy_with_from(self):
        instruction = Copy('--from=0 source_path_a/something.py /')

        expected = {
            "src": ["source_path_a/something.py"], "dest": "/", "chown": None, "from": "0"
        }
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_copy_with_multiple_sources(self):
        instruction = Copy('source_path_a/something.py source_path_b/something.py /somewhere')

        expected = {
            "src": ["source_path_a/something.py", "source_path_b/something.py"],
            "dest": "/somewhere",
            "chown": None,
            "from": None
        }
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_copy_with_multiple_sources_and_chown(self):
        instruction = Copy('--chown=user:group source_path_a/something.py source_path_b/something.py /somewhere')

        expected = {
            "src": ["source_path_a/something.py", "source_path_b/something.py"],
            "dest": "/somewhere",
            "chown": "user:group",
            "from": None
        }
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_copy_exec_form(self):
        instruction = Copy('["source_path_a/something.py", "/"]')

        expected = {
            "src": ["source_path_a/something.py"], "dest": "/", "chown": None, "from": None
        }
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_copy_exec_form_multiple_sources(self):
        instruction = Copy('["source_path_a/something.py", "source_path_b/something.py", "/"]')

        expected = {
            "src": ["source_path_a/something.py", "source_path_b/something.py"],
            "dest": "/",
            "chown": None,
            "from": None
        }
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_copy_exec_form_multiple_sources_and_chown(self):
        instruction = Copy('--chown=user:group ["source_path_a/something.py", "source_path_b/something.py", "/"]')

        expected = {
            "src": ["source_path_a/something.py", "source_path_b/something.py"],
            "dest": "/",
            "chown": "user:group",
            "from": None
        }
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_copy_exec_form_multiple_sources_and_chown_and_from(self):
        instruction = Copy(
            '--from=somestage --chown=user:group ["source_path_a/something.py", "source_path_b/something.py", "/"]')

        expected = {
            "src": ["source_path_a/something.py", "source_path_b/something.py"],
            "dest": "/",
            "chown": "user:group",
            "from": "somestage"
        }
        self.typical_positive_instruction_assertions(instruction, expected)

    def test_invalid_option_after_dest(self):
        instruction = Copy('a b --from=0')

        expected = {
            "src": ["a", "b"],
            "dest": "--from=0"
        }
        self.typical_positive_instruction_assertions(instruction, expected)
