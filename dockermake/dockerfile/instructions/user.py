import pyparsing as pp

from dockermake.dockerfile.instructions.instruction_base import InstructionBase


class User(InstructionBase):
    def build_grammar(self):
        user = self.pp_word(without=":").setResultsName("user")
        group = self.pp_word().setResultsName("group")
        grammar = user + pp.Optional(pp.Suppress(":") + group)

        return grammar
