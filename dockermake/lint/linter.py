import logging

from dockermake.lint.rules.general import GeneralRules
from dockermake.lint.rules.every_stage import EveryStageRules
from dockermake.lint.rules.builder_stages import BuilderStagesRules
from dockermake.lint.rules.last_stage import LastStageRules

from dockermake.lint.linting_exception import LintingException

from dockermake.utils import display


class DockerfileLint:
    """Linting of Dockerfile against common coding style rules."""

    def __init__(self, dockerfile, exit_on_errors=True, exclude=None):
        self.dockerfile = dockerfile
        self.exit_on_errors = exit_on_errors
        self.exclude = []
        if exclude and isinstance(exclude, list):
            for exclude_arg in exclude:
                self.exclude += [rule.strip() for rule in exclude_arg.split(",")]
        logging.info(exclude)
        self.warnings = list()
        self.errors = list()

    def lint(self):
        display.info("Step 0 : Linting \"%s\"" % str(self.dockerfile))

        self.validate_syntax()
        self.validate_rules()

        for error in self.errors:
            display.error("---> %s" % error)

        with_warnings = ""
        if self.warnings:
            for warning in self.warnings:
                display.warn("---> [WARNING] %s" % warning)
            if not self.errors:
                with_warnings = " with warning(s)"

        result = "---> %s%s" % ("FAILED" if self.errors else "OK", with_warnings)
        if self.errors:
            display.error(result)
        else:
            display.info(result, color="green")

        if self.exit_on_errors and self.errors:
            raise LintingException("Linting failed")

    def validate_syntax(self):
        for instruction in self.dockerfile.instructions:
            for syntax_error in instruction.syntax_errors:
                self.errors.append(syntax_error)

    def validate_rules(self):
        rule_sets = [GeneralRules, EveryStageRules, LastStageRules, BuilderStagesRules]
        for rule_set in rule_sets:
            self.validate_rule_set(rule_set)

    def validate_rule_set(self, rule_set):
        rule_class = rule_set(self.dockerfile)
        rules = self.gather_rules(rule_class, self.exclude)
        self._validate_rules(rule_class, rules)

    @staticmethod
    def gather_rules(rule_class, exclude=None):
        exclude = exclude or []
        rules = list()
        for name in sorted(dir(rule_class)):
            if callable(getattr(rule_class, name)):
                if name.startswith("rule") and name not in exclude:
                    rules.append(name)
        logging.debug("Loaded following rules of %s: %s", rule_class.__class__.__name__, rules)
        return rules

    def _validate_rules(self, rule_class, rules):
        for rule in rules:
            getattr(rule_class, rule)()
        self.errors += rule_class.errors
        self.warnings += rule_class.warnings
