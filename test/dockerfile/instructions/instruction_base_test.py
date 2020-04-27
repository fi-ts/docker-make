from dockermake.dockerfile.instructions.instruction_base import InstructionBase
from test.dockerfile.instructions import InstructionTest


class InstructionBaseTest(InstructionTest):
    def test_pp_path_absolute(self):
        path = InstructionBase.pp_path().setResultsName("path")

        result = path.parseString("/a/path/to/somewhere")

        self.assertEqual(result.get("path"), "/a/path/to/somewhere")

    def test_pp_path_relative(self):
        path = InstructionBase.pp_path().setResultsName("path")

        result = path.parseString("a/path/to/somewhere")

        self.assertEqual(result.get("path"), "a/path/to/somewhere")

    def test_pp_path_without_separator(self):
        path = InstructionBase.pp_path().setResultsName("path")

        result = path.parseString("apath")

        self.assertEqual(result.get("path"), "apath")

    def test_pp_path_root(self):
        path = InstructionBase.pp_path().setResultsName("path")

        result = path.parseString("/")

        self.assertEqual(result.get("path"), "/")
