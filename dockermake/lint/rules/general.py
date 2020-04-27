from email.utils import parseaddr

from dockermake.registries.registries import Registries
from dockermake.dockerfile.instructions import Keywords
from dockermake.dockerfile.instructions.exec_form_base import ExecFormBase
from dockermake.lint.rules import RulesBase


class GeneralRules(RulesBase):
    def rule0_0(self):
        """FROM must occur at least once"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.FROM)
        if not instructions:
            self.error()

    def rule0_1_2(self):
        """Do not mix LABEL maintainer and MAINTAINER"""
        maintainer_labels = self.dockerfile.get_maintainer_labels(True)
        maintainer_instructions = self.dockerfile.get_instructions_of_type(Keywords.MAINTAINER)
        if maintainer_labels and maintainer_instructions:
            self.error()

    def rule0_1_4(self):
        """LABEL maintainer is recommended over MAINTAINER"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.MAINTAINER)
        if instructions:
            self.warning()

    def rule0_1_5(self):
        """LABEL maintainer must be lowercase"""
        instructions = self.dockerfile.get_maintainer_labels(True)
        for label in instructions:
            if not label.contains("maintainer", False):
                self.error(line_number=label.physical_line_number)

    def rule0_1_6(self):
        """LABEL maintainer requires a mail address"""
        instructions = self.dockerfile.get_maintainer_labels(True)
        for label in instructions:
            maintainers = label.value_of("maintainer", False)
            if maintainers:
                for maintainer in maintainers.split(","):
                    if "@" not in maintainer:
                        self.error(line_number=label.physical_line_number)

    def rule1(self):
        """FROM must be the first instruction (only ARG can precede FROM)"""
        for instruction in self.dockerfile.get_instructions():
            if instruction.get_type() == Keywords.ARG:
                continue
            if instruction.get_type() == Keywords.FROM:
                break
            self.error()
            break

    def rule2(self):
        """FROM must point to an allowed registry: %s"""
        if not Registries().push_only_to_defined_registries:
            return
        allowed_registries = Registries().get().keys()
        if allowed_registries:
            instructions = self.dockerfile.get_instructions_of_type(Keywords.FROM)
            for instruction in instructions:
                if instruction.registry not in allowed_registries:
                    self.error(substitution=list(allowed_registries), line_number=instruction.physical_line_number)

    def rule3(self):
        """FROM must point to a username"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.FROM)
        for instruction in instructions:
            if instruction.username is None:
                self.error(line_number=instruction.physical_line_number)

    def rule4(self):
        """FROM must point to a name with at least 2 characters, actual: %s"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.FROM)
        for instruction in instructions:
            if instruction.image and len(instruction.image) < 2:
                self.error(substitution=instruction.image, line_number=instruction.physical_line_number)

    def rule5(self):
        """FROM must point to a tag"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.FROM)
        for instruction in instructions:
            if instruction.tag is None:
                self.error(line_number=instruction.physical_line_number)

    def rule6(self):
        """ADD is prohibited"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.ADD)
        if instructions:
            self.error()

    def rule8(self):
        """CMD or ENTRYPOINT must be the last instruction if present"""
        cmd_index = self.dockerfile.get_last_index_of(Keywords.CMD)
        entrypoint_index = self.dockerfile.get_last_index_of(Keywords.ENTRYPOINT)
        last_index = self.dockerfile.get_instruction_count() - 1
        if ((cmd_index != -1 or entrypoint_index != -1)
                and cmd_index != last_index
                and entrypoint_index != last_index):
            self.error()

    def rule9(self):
        """RUN sudo is prohibited"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.RUN)
        for instruction in instructions:
            if instruction.argument.strip().startswith("sudo"):
                self.error(line_number=instruction.physical_line_number)

    def rule10(self):
        """Lines longer than 100 characters"""
        physical_lines = self.dockerfile.get_physical_lines()
        line_number = 0
        for physical_line in physical_lines:
            line_number += 1
            if len(physical_line) > 100:
                self.warning(line_number=line_number)

    def rule11_0(self):
        """AND (&&) / OR (||) control operators must be in front of each concerned line for multi-line RUN commands"""
        physical_lines = self.dockerfile.get_physical_lines()
        line_number = 0
        for physical_line in physical_lines:
            if physical_line.strip().startswith("#"):
                continue
            and_index = physical_line.strip().find("&&")
            or_index = physical_line.strip().find("||")
            line_number += 1
            if and_index > 0 or or_index > 0:
                self.warning(line_number=line_number)

    def rule11_1(self):
        """AND (&&) / OR (||) control operators should be indented by a single white space in front of each """ \
        """concerned line for multi-line RUN commands"""
        physical_lines = self.dockerfile.get_physical_lines()
        line_number = 0
        for physical_line in physical_lines:
            if physical_line.strip().startswith("#"):
                continue
            and_index = physical_line.find("&&")
            or_index = physical_line.find("||")
            line_number += 1
            if abs(and_index) != 1 or abs(or_index) != 1:
                self.warning(line_number=line_number)

    def rule12_1(self):
        """CMD argument(s) must be enclosed with " instead of '"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.CMD)
        for cmd in instructions:
            if not ExecFormBase.is_pure_double_quoted_exec_form(cmd):
                self.error(line_number=cmd.physical_line_number)

    def rule12_2(self):
        """ENTRYPOINT argument(s) must be enclosed with " instead of '"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.ENTRYPOINT)
        for entrypoint in instructions:
            if not ExecFormBase.is_pure_double_quoted_exec_form(entrypoint):
                self.error(line_number=entrypoint.physical_line_number)

    def rule12_3(self):
        """VOLUME argument(s) must be enclosed with " instead of '"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.VOLUME)
        for volume in instructions:
            if not ExecFormBase.is_pure_double_quoted_exec_form(volume):
                self.error(line_number=volume.physical_line_number)

    def rule13_0(self):
        """LABEL maintainer must be in the form name <name@mail.com>"""
        instructions = self.dockerfile.get_maintainer_labels(False)
        for instruction in instructions:
            maintainers = instruction.value_of("maintainer", False)
            if maintainers:
                for maintainer in maintainers.split(","):
                    name, email = parseaddr(maintainer)
                    if not name:
                        self.error(line_number=instruction.physical_line_number)
                    if not email:
                        self.error(line_number=instruction.physical_line_number)

    def rule13_1(self):
        """MAINTAINER must be in the form name <name@mail.com>"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.MAINTAINER)
        for maintainer_instruction in instructions:
            if maintainer_instruction.maintainers:
                for maintainer in maintainer_instruction.maintainers:
                    name, email = parseaddr(maintainer)
                    if not name:
                        self.error(line_number=maintainer_instruction.physical_line_number)
                    if not email:
                        self.error(line_number=maintainer_instruction.physical_line_number)

    def rule14(self):
        """no trailing whitespaces"""
        physical_lines = self.dockerfile.get_physical_lines()
        line_number = 0
        for physical_line in physical_lines:
            line_number += 1
            physical_line = physical_line.lstrip()
            if physical_line != physical_line.rstrip():
                self.warning(line_number=line_number)

    def rule15(self):
        """exactly one newline at the end"""
        physical_lines = self.dockerfile.get_physical_lines()
        if len(physical_lines) > 1 and physical_lines[-2].strip() == "" and physical_lines[-1].strip() == "":
            self.warning()
