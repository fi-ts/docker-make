import pyparsing as pp

from dockermake.dockerfile.instructions.instruction_base import InstructionBase


class Arg(InstructionBase):
    def build_grammar(self):
        name = self.pp_word(without="=").setResultsName("name")
        default = pp.Optional(pp.Suppress("=") + self.pp_word(), default="").setResultsName("default")
        default.setParseAction(' '.join)

        grammar = pp.Combine(name + default)

        return grammar
