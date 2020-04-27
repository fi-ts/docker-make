from abc import ABCMeta
import inspect


class RulesBase:
    __metaclass__ = ABCMeta

    def __init__(self, dockerfile):
        self.dockerfile = dockerfile
        self.errors = []
        self.warnings = []

    def error(self, line_number=None, substitution=None):
        msg = self._message_base(line_number, substitution)
        self.errors.append(msg)

    def warning(self, line_number=None, substitution=None):
        msg = self._message_base(line_number, substitution)
        self.warnings.append(msg)

    @staticmethod
    def get_rule_info(stack_pos=3, substitution=None):
        """
        Get the documentation for the method at stack_pos.
        stack_pos = 0 => Is documentation of this method
        stack_pos = 1 => Is documentation of the method that called this method
        ...

        Warning: This method is not safe when altering the stack_pos arbitrarily.
        """
        stack = inspect.stack()
        try:
            the_class = stack[stack_pos][0].f_locals["self"].__class__
            the_method = stack[stack_pos][0].f_code.co_name
        except IndexError:
            return "No doc found"
        doc = getattr(the_class, the_method).__doc__
        if substitution:
            doc = doc % substitution
        return doc, the_method

    @classmethod
    def _message_base(cls, line_number, substitution):
        doc, method_name = RulesBase.get_rule_info(substitution=substitution)

        if line_number:
            additional_info = "%s, line: %d" % (method_name, line_number)
        else:
            additional_info = method_name

        return "%s (%s)" % (doc, additional_info)
