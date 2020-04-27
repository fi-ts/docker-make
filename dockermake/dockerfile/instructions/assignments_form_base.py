from abc import ABCMeta, abstractmethod
import pyparsing as pp

from dockermake.dockerfile.instructions.instruction_base import InstructionBase


class AssignmentsFormBase(InstructionBase, metaclass=ABCMeta):
    """Abstract base class for instructions that demand an assignment form"""

    __metaclass__ = ABCMeta

    def __init__(self, argument, physical_line_number=None):
        self.assignments = None
        super(AssignmentsFormBase, self).__init__(argument, physical_line_number=physical_line_number)

    @staticmethod
    def _assignments_form_grammar(allow_old_style=True):
        assignments = AssignmentsFormBase._build_assignments_grammar()

        if allow_old_style:
            old_style = AssignmentsFormBase._build_old_style_assignment()
            grammar = assignments | old_style
        else:
            grammar = assignments

        return grammar

    @staticmethod
    def _build_assignments_grammar():
        key = InstructionBase.pp_word(without="=", unquote=True) + ~pp.FollowedBy(pp.White())
        value = InstructionBase.pp_word(unquote=True)
        assignment = (key + pp.Combine(pp.Suppress("=") + pp.Optional(value, default=""))).setName("assignment")
        assignments = pp.OneOrMore(assignment).setParseAction(InstructionBase.dictionize)
        assignments = assignments.setResultsName("assignments")
        return assignments

    @staticmethod
    def _build_old_style_assignment():
        key = InstructionBase.pp_word(unquote=True)
        value = pp.OneOrMore(InstructionBase.pp_word()).setParseAction(" ".join)
        assignment = (key + value).setName("old style assignment")
        assignment = assignment.setParseAction(InstructionBase.dictionize)
        assignment = assignment.setResultsName("assignments")
        return assignment

    @abstractmethod
    def build_grammar(self):
        raise NotImplementedError

    def contains(self, key, ignore_case):
        return self.value_of(key, ignore_case) is not None

    def value_of(self, requested_key, ignore_case):
        if self.assignments:
            for key, value in self.assignments.items():
                if (ignore_case and key.lower() == requested_key.lower()) or key == requested_key:
                    return value
        return None
