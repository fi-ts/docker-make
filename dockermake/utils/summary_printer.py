import json
import tabulate

from dockermake.lint.linter import DockerfileLint
from dockermake.lint.rules.general import GeneralRules
from dockermake.lint.rules.every_stage import EveryStageRules
from dockermake.lint.rules.builder_stages import BuilderStagesRules
from dockermake.lint.rules.last_stage import LastStageRules
from dockermake.utils import display

# Until now, tabulate (0.8.2) did not release github flavored table styles... as long as we are waiting, here is
# the workaround
# pylint: disable=protected-access
tabulate._table_formats.update({
    "github":
        tabulate.TableFormat(lineabove=tabulate.Line("|", "-", "|", "|"),
                             linebelowheader=tabulate.Line("|", "-", "|", "|"),
                             linebetweenrows=None,
                             linebelow=None,
                             headerrow=tabulate.DataRow("|", "|", "|"),
                             datarow=tabulate.DataRow("|", "|", "|"),
                             padding=1,
                             with_header_hide=["lineabove"]),
})


class SummaryPrinter:
    @staticmethod
    def print_tag_list(build_summary):
        display.info("")
        for build in build_summary:
            display.info(build["name"].strip() + ":")
            for tag in build["build-tags"]:
                display.info(tag)

    @classmethod
    def print_full_build_summary(cls, build_summary):
        display.info("")
        display.info("Markdown Summary (Gitlab compatible):")
        display.info("")
        display.info("# Build Summary")
        display.info("")
        cls._print_table_of_contents(build_summary)
        for build in build_summary:
            cls._print_build_name(build.get("name"))
            cls._print_build_args(build.get("build-args"))
            cls._print_build_labels(build.get("build-labels"))
            cls._print_build_tags(build.get("build-tags"))
            cls._print_build_image_properties(build.get("image-properties"))
            cls._print_build_digests(build.get("digest"))

    @staticmethod
    def _print_table_of_contents(build_summary):
        for i, build in enumerate(build_summary):
            index = str(i + 1)
            build_name = build["name"].strip()
            anchor = build_name.strip().lower().replace(" ", "-")
            display.info("%s. [%s](#%s)" % (index, build_name, anchor))
        display.info("")

    @staticmethod
    def _print_build_name(build_name):
        display.info("## " + build_name)
        display.info("")

    @staticmethod
    def _print_build_args(build_args):
        display.info("### Build Arguments")
        display.info("")
        if build_args:
            table = [build_arg.split("=") for build_arg in build_args]
            display.info(tabulate.tabulate(table, ["Key", "Value"], tablefmt="github"))
        else:
            display.info("None")
        display.info("")

    @staticmethod
    def _print_build_labels(build_labels):
        display.info("### Build Labels")
        display.info("")
        if build_labels:
            for build_label in build_labels:
                display.info("- " + build_label)
        else:
            display.info("None")
        display.info("")

    @staticmethod
    def _print_build_tags(build_tags):
        display.info("### Build Tags")
        display.info("")
        if build_tags:
            for build_tag in build_tags:
                display.info("- " + build_tag)
        else:
            display.info("None")
        display.info("")

    @staticmethod
    def _print_build_image_properties(image_properties):
        display.info("### Image Properties")
        display.info("")
        display.info("```")
        display.info(json.dumps(image_properties, indent=4, sort_keys=True))
        display.info("```")
        display.info("")

    @staticmethod
    def _print_build_digests(digest):
        display.info("### Repository Digests")
        display.info("")
        # digest: "sha256:d85914d547a6c92faa39ce7058bd7529baacab7e0cd4255442b04577c4d1f424"
        if digest is None:
            display.info("None")
        else:
            display.info('digest: "' + digest + '"')
        display.info("")

    @classmethod
    def print_rule_summary(cls):
        cls._print_general_rules()
        cls._print_every_stage_rules()
        cls._print_last_stage_rules()
        cls._print_builder_stages_rules()

    @classmethod
    def _print_general_rules(cls):
        display.info("# General Rules")
        cls._print_rules(GeneralRules(None))

    @classmethod
    def _print_every_stage_rules(cls):
        display.info("# Every Stage Rules")
        cls._print_rules(EveryStageRules(None))

    @classmethod
    def _print_last_stage_rules(cls):
        display.info("# Last Stage Rules")
        cls._print_rules(LastStageRules(None))

    @classmethod
    def _print_builder_stages_rules(cls):
        display.info("# Builder Stages Rules")
        cls._print_rules(BuilderStagesRules(None))

    @staticmethod
    def _print_rules(rule_class):
        display.info("")
        for i, rule in enumerate(DockerfileLint.gather_rules(rule_class)):
            display.info(str(i + 1) + ". " + getattr(rule_class, rule).__doc__ + " (" + rule + ")")
        display.info("")
