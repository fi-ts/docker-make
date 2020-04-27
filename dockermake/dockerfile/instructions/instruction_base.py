from abc import ABCMeta, abstractmethod
import pyparsing as pp

from dockermake.dockerfile.instructions import get_keyword_from_class

pp.ParserElement.enablePackrat()


class InstructionBase:
    """Abstract base class for all Instructions"""

    __metaclass__ = ABCMeta

    def __init__(self, argument, physical_line_number=None):
        self.argument = argument
        self.physical_line_number = physical_line_number
        self.stage_name = None
        self.syntax_errors = list()

        self.grammar = self.build_grammar()
        parsed_results = self._parse_instruction()
        self._set_grammar_attributes(parsed_results)

    def _parse_instruction(self):
        result = dict()
        try:
            result = self.grammar.parseString(self.argument, parseAll=True)
        except pp.ParseException as exception:
            msg = "{} (at line {}, position {} of the argument)".format(exception.msg, self.physical_line_number,
                                                                        exception.col)
            self.append_syntax_error(self.argument, hint=msg)
        return result

    def _set_grammar_attributes(self, parse_result):
        """
        Writes all the result names defined in the grammar as attributes into the instruction class.
        """
        for var_name in self._find_all_result_names(self.grammar):
            var_value = parse_result.get(var_name, None)
            if isinstance(var_value, pp.ParseResults):
                var_value = var_value.asList()
            setattr(self, var_name, var_value)

    @classmethod
    def _find_all_result_names(cls, expr):
        """
        pyparsing will not include a key in the parse result if there was no match, even though we want to set at least
        a None value for this variable in the class. Therefore, we look through all expressions of the grammar and
        save the defined result names in a separate list, which we can use for setting up the instruction class.
        """
        result_names = list()
        if expr.resultsName:
            result_names.append(expr.resultsName)
        if hasattr(expr, 'expr'):
            result_names += cls._find_all_result_names(expr.expr)
        elif hasattr(expr, 'exprs'):
            for child_expr in expr.exprs:
                result_names += cls._find_all_result_names(child_expr)
        return result_names

    @abstractmethod
    def build_grammar(self):
        raise NotImplementedError

    def get_type(self):
        return self.__class__

    def get_keyword(self):
        return get_keyword_from_class(self.get_type())

    def append_syntax_error(self, argument, hint=""):
        if hint:
            msg = "%s instruction with argument \"%s\" is invalid: %s" % (self.get_keyword(), argument, hint)
        else:
            msg = "%s instruction with argument \"%s\" is invalid." % (self.get_keyword(), argument)
        self.syntax_errors.append(msg)

    @staticmethod
    def pp_word(without=None, unquote=False):
        quotes = InstructionBase.pp_quoted(unquote=unquote)
        word = quotes | (~pp.Literal('"') + pp.Word(pp.printables, excludeChars=without))
        word = word.setName("word")
        if without:
            formatted_without = ", ".join(['"' + character + '"' for character in without])
            word.setName("word without the characters %s" % formatted_without)
        return word

    @staticmethod
    def pp_quoted(quote='"', unquote=None):
        return pp.QuotedString(quote, unquoteResults=unquote, escChar="\\").setName("quoted string")

    @staticmethod
    def pp_path():
        relative_path = pp.Combine(
            pp.delimitedList(InstructionBase.pp_word(without="/"), delim="/", combine=True) +
            pp.Optional(pp.Word("/"))
        )
        absolute_path = pp.Combine("/" + pp.Optional(relative_path))
        return (relative_path ^ absolute_path).setName("path")

    @staticmethod
    def pp_optional_parameter(name, value, default):
        option_name = pp.Combine("--" + name.replace("_", "-") + "=")
        if default:
            option = pp.Optional(pp.Suppress(option_name) + value, default=default).setResultsName(name)
            option.setParseAction(lambda tokens: tokens[0])  # converts token list from optional group to string
        else:
            value = value.setResultsName(name)
            option = pp.Optional(pp.Suppress(option_name) + value)
        return option.setName("option")

    @staticmethod
    def dictionize(tokens):
        iterator = iter(tokens)
        result = dict()
        for token in iterator:
            result[token] = next(iterator)
        return result

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "%s %s" % (self.get_keyword(), self.argument)
