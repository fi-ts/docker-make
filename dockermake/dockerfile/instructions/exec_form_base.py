from abc import ABCMeta, abstractmethod
import pyparsing as pp

from dockermake.dockerfile.instructions.instruction_base import InstructionBase
from dockermake.utils.helpers import enum


class ExecFormBase(InstructionBase, metaclass=ABCMeta):
    """Abstract base class for instructions that demand exec form arguments"""

    __metaclass__ = ABCMeta

    QuotingType = enum('SINGLE', 'DOUBLE', 'BOTH')
    SINGLE_QUOTED_STRING = InstructionBase.pp_quoted(quote="'", unquote=True).setName("single quoted string")
    DOUBLE_QUOTED_STRING = InstructionBase.pp_quoted(unquote=True).setName("double quoted string")

    @staticmethod
    def _exec_form_grammar(allow_shell_form=True):
        pure_exec_form = ExecFormBase._pure_exec_form()
        shell_form = ExecFormBase._shell_form()

        if allow_shell_form:
            grammar = pure_exec_form ^ shell_form
        else:
            grammar = pure_exec_form

        return grammar

    @staticmethod
    def _pure_exec_form(quoting_type=QuotingType.BOTH):
        start = "["
        argument = ExecFormBase._argument_from_quoting_type(quoting_type).setName("argument")
        argument = argument.setResultsName("arguments", listAllMatches=True)
        arguments = pp.delimitedList(argument, delim=",").setName("arguments")
        end = "]"

        exec_form = (start + arguments + end).setName("exec form")

        return exec_form

    @staticmethod
    def _argument_from_quoting_type(quoting_type):
        if quoting_type == ExecFormBase.QuotingType.SINGLE:
            return ExecFormBase.SINGLE_QUOTED_STRING
        if quoting_type == ExecFormBase.QuotingType.DOUBLE:
            return ExecFormBase.DOUBLE_QUOTED_STRING
        if quoting_type == ExecFormBase.QuotingType.BOTH:
            return (ExecFormBase.SINGLE_QUOTED_STRING | ExecFormBase.DOUBLE_QUOTED_STRING).setName("quoted string")
        raise Exception("Unsupported exec form quoting type: %s" % quoting_type)

    @staticmethod
    def _shell_form():
        anything_combined = pp.Combine(pp.ZeroOrMore(pp.Word(pp.printables)), joinString=" ", adjacent=False)
        shell_form = ~pp.Literal("[") + anything_combined
        shell_form = shell_form.setResultsName("arguments").setName("shell form")
        return shell_form

    @staticmethod
    def is_pure_double_quoted_exec_form(instruction):
        # first figure out if we have an exec form
        regular_grammar = ExecFormBase._pure_exec_form(quoting_type=ExecFormBase.QuotingType.BOTH)
        is_pure_exec_form = False
        try:
            regular_grammar.parseString(instruction.argument, parseAll=True)
            is_pure_exec_form = True
        except pp.ParseException:
            pass
        if is_pure_exec_form:
            # then check if it contains only of double quoted string
            only_double = ExecFormBase._pure_exec_form(quoting_type=ExecFormBase.QuotingType.DOUBLE)
            try:
                only_double.parseString(instruction.argument, parseAll=True)
            except pp.ParseException:
                return False
        return True

    @abstractmethod
    def build_grammar(self):
        raise NotImplementedError
