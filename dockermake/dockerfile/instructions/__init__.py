import importlib
from inspect import isabstract
import pkgutil
import sys

from dockermake.utils.helpers import dockerfile_keyword

BASE_MODULE = importlib.import_module(__name__)
MODULE_PREFIX = BASE_MODULE.__name__ + "."


def _dynamically_load():
    module_names = [m[1] for m in pkgutil.iter_modules(__path__, MODULE_PREFIX)]

    # this is for pyinstaller
    # see https://github.com/pyinstaller/pyinstaller/issues/1905
    toc = set()
    for importer in pkgutil.iter_importers('dockermake'):
        if hasattr(importer, 'toc'):
            toc |= importer.toc
    for elm in toc:
        if elm.startswith(MODULE_PREFIX):
            module_names.append(elm)

    for name in module_names:
        try:
            importlib.import_module(name)
        except ImportError as msg:
            raise Exception("could not load module %s: %s" % (name, msg))


def _get_keywords():
    keywords = dict()
    instruction_base_module = sys.modules[MODULE_PREFIX + "instruction_base"]
    instruction_base_class = getattr(instruction_base_module, "InstructionBase")
    for instruction_class in _get_all_subclasses(instruction_base_class):
        keyword = get_keyword_from_class(instruction_class)
        keywords[keyword] = instruction_class
    return keywords


def _get_all_subclasses(cls):
    all_subclasses = []
    for subclass in cls.__subclasses__():
        if not isabstract(subclass):
            all_subclasses.append(subclass)
        all_subclasses.extend(_get_all_subclasses(subclass))
    return all_subclasses


def get_keyword_from_class(instruction_class):
    return instruction_class.__name__.upper()


def get_class_from_keyword(keyword):
    return Keywords.mapping[keyword]


# We load the instruction classes dynamically in order not to have to define
# all the instructions for the factory statically. New instructions will
# automatically be picked up and the keyword (class_name.upper()) will be added accordingly.

_dynamically_load()
Keywords = dockerfile_keyword(**_get_keywords())


class InstructionFactory:
    @staticmethod
    def create_from_keyword(keyword, argument, physical_line_number):
        return Keywords.mapping[keyword](argument, physical_line_number)
