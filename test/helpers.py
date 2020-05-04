import argparse
from contextlib import contextmanager
import os
from io import StringIO
import sys

from dockermake.lint.rules.general import GeneralRules
from dockermake.lint.rules.every_stage import EveryStageRules
from dockermake.lint.rules.builder_stages import BuilderStagesRules
from dockermake.lint.rules.last_stage import LastStageRules

from dockermake.dockerfile.dockerfile import Dockerfile

from dockermake.registries.registries import Registries


def get_rule_wrapper(rule_class, context):
    dockerfile = Dockerfile._parse(context)
    return rule_class(dockerfile)


def get_general_wrapper(context):
    return get_rule_wrapper(GeneralRules, context)


def get_last_stage_wrapper(context):
    return get_rule_wrapper(LastStageRules, context)


def get_every_stage_wrapper(context):
    return get_rule_wrapper(EveryStageRules, context)


def get_builder_stages_wrapper(context):
    return get_rule_wrapper(BuilderStagesRules, context)


def get_mock_dir():
    return os.path.join(os.path.dirname(__file__), "mock")


def mock_registries():
    Registries().load(argparse.Namespace(registries_file=os.path.join(get_mock_dir(), "registries.yaml"),
                                         push_only_to_specific_git_projects=False,
                                         push_only_to_defined_registries=True))


def is_sublist(container, member):
    sub_set = False
    if not member:
        sub_set = True
    elif member == container:
        sub_set = True
    elif len(member) > len(container):
        sub_set = False
    else:
        for i in range(len(container)):
            if container[i] == member[0]:
                n = 1
                while (n < len(member)) and (container[i + n] == member[n]):
                    n += 1
                if n == len(member):
                    sub_set = True
    return sub_set


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err
