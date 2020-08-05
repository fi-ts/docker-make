from dockermake.dockerfile.instructions import Keywords

from dockermake.lint.rules import RulesBase


class LastStageRules(RulesBase):
    def rule0_1_0(self):
        """LABEL maintainer must occur at most once in last stage"""
        instructions = self.dockerfile.get_maintainer_labels(True, stage=self.dockerfile.get_last_stage())
        if len(instructions) > 1:
            self.error(self.rule0_1_0)

    def rule0_1_1(self):
        """MAINTAINER must occur at most once in last stage"""
        instructions = self.dockerfile.get_instructions_of_type(
            Keywords.MAINTAINER, stage=self.dockerfile.get_last_stage()
        )
        if len(instructions) > 1:
            self.error(self.rule0_1_1)

    def rule0_1_3(self):
        """Either LABEL maintainer or MAINTAINER is mandatory in last stage"""
        last_stage = self.dockerfile.get_last_stage()
        maintainer_labels = self.dockerfile.get_maintainer_labels(True, stage=last_stage)
        maintainer_instructions = self.dockerfile.get_instructions_of_type(Keywords.MAINTAINER, stage=last_stage)
        if not maintainer_labels and not maintainer_instructions:
            self.error(self.rule0_1_3)

    def rule0_2(self):
        """EXPOSE must occur at most once in last stage"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.EXPOSE, stage=self.dockerfile.get_last_stage())
        if len(instructions) > 1:
            self.error(self.rule0_2)

    def rule0_3(self):
        """ENTRYPOINT must occur at most once in last stage"""
        instructions = self.dockerfile.get_instructions_of_type(
            Keywords.ENTRYPOINT, stage=self.dockerfile.get_last_stage()
        )
        if len(instructions) > 1:
            self.error(self.rule0_3)

    def rule0_4(self):
        """CMD must occur at most once in last stage"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.CMD, stage=self.dockerfile.get_last_stage())
        if len(instructions) > 1:
            self.error(self.rule0_4)

    def rule0_5(self):
        """VOLUME must occur at most once in last stage"""
        instructions = self.dockerfile.get_instructions_of_type(Keywords.VOLUME, stage=self.dockerfile.get_last_stage())
        if len(instructions) > 1:
            self.error(self.rule0_5)

    def rule7(self):
        """CMD must be after ENTRYPOINT if both are specified in last stage"""
        last_stage = self.dockerfile.get_last_stage()
        cmd_index = self.dockerfile.get_last_index_of(Keywords.CMD, stage=last_stage)
        entrypoint_index = self.dockerfile.get_last_index_of(Keywords.ENTRYPOINT, stage=last_stage)
        if cmd_index != -1 and entrypoint_index != -1 and entrypoint_index > cmd_index:
            self.error(self.rule7)
