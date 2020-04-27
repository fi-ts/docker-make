from dockermake.dockerfile.instructions.instruction_base import InstructionBase


class Workdir(InstructionBase):
    def build_grammar(self):
        grammar = self.pp_path().setResultsName("workdir")

        return grammar
