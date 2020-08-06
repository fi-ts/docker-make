from abc import ABCMeta
import inspect


class RulesBase(metaclass=ABCMeta):
    def __init__(self, dockerfile):
        self.dockerfile = dockerfile
        self.errors = []
        self.warnings = []

    def error(self, caller=None, line_number=None, substitution=None):
        msg = self._message_base(caller, line_number, substitution)
        self.errors.append(msg)

    def warning(self, caller=None, line_number=None, substitution=None):
        msg = self._message_base(caller, line_number, substitution)
        self.warnings.append(msg)

    @classmethod
    def _message_base(cls, caller, line_number, substitution):
        doc = "No doc found"
        method_name = "-"

        if caller:
            doc = caller.__doc__
            if substitution:
                doc = doc % substitution
            method_name = caller.__name__

        if line_number:
            additional_info = "%s, line: %d" % (method_name, line_number)
        else:
            additional_info = method_name

        return "%s (%s)" % (doc, additional_info)
