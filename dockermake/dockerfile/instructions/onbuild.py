import pyparsing as pp

from dockermake.dockerfile.instructions.instruction_base import InstructionBase
from dockermake.dockerfile.instructions import get_class_from_keyword


class OnBuild(InstructionBase):
    def build_grammar(self):
        forbidden_keywords = ~pp.Literal("ONBUILD") + ~pp.Literal("MAINTAINER") + ~pp.Literal("FROM")
        keyword = (forbidden_keywords + pp.Word(pp.srange("[A-Z]")).setResultsName("onbuild").setName("keyword"))
        grammar = keyword + pp.OneOrMore(pp.White()) + pp.restOfLine.setResultsName("onbuild_argument")

        try:
            result = grammar.parseString(self.argument, parseAll=True)
            onbuild_command = result.get("onbuild", None)
            onbuild_argument = result.get("onbuild_argument", "")

            if onbuild_command:
                instruction_class = None
                try:
                    instruction_class = get_class_from_keyword(onbuild_command)
                except KeyError:
                    self.append_syntax_error(
                        self.argument, hint="Instruction of type " + onbuild_command + " does not exist."
                    )

                if instruction_class:
                    instruction = instruction_class(onbuild_argument, self.physical_line_number)
                    foreign_grammar = instruction.build_grammar()
                    grammar = keyword + foreign_grammar

        except pp.ParseException:
            # This will be reraised again by the instruction base anyway
            pass

        return grammar
