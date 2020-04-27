import pyparsing as pp

from dockermake.dockerfile.instructions.instruction_base import InstructionBase


class Expose(InstructionBase):
    def build_grammar(self):
        port = self.pp_word()
        grammar = pp.OneOrMore(port).setResultsName("ports")

        return grammar
