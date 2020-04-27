import sys

from dockermake.dockerfile.instructions import InstructionFactory
from dockermake.dockerfile.instructions import Keywords

this_module = sys.modules[__name__]


def generate(name):
    def func(argument, physical_line_number=None):
        return InstructionFactory.create_from_keyword(name, argument, physical_line_number=physical_line_number)

    return func


for keyword in Keywords.list:
    class_name = Keywords.mapping[keyword].__name__
    setattr(this_module, class_name, generate(keyword))
