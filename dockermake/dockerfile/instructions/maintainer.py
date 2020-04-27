import pyparsing as pp
from dockermake.dockerfile.instructions.instruction_base import InstructionBase


class Maintainer(InstructionBase):
    def build_grammar(self):
        maintainer = pp.OneOrMore(self.pp_word(without=",")).setParseAction(" ".join)
        maintainers = pp.delimitedList(maintainer, delim=",").setResultsName("maintainers")

        grammar = maintainers

        return grammar
