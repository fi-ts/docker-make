import logging
import os

from dockermake.dockerfile.instructions import Keywords
from dockermake.dockerfile.instructions import InstructionFactory
from dockermake.lint.linter import DockerfileLint
from dockermake.dockerfile.logical_line_extractor import LogicalLineExtractor


class Dockerfile:
    def __init__(self):
        self.path = None
        self.physical_lines = list()
        self.logical_lines = list()
        self.instructions = list()
        self.stages = list()

    @staticmethod
    def load(working_directory_path, dockerfile_name):
        dockerfile_path = os.path.join(working_directory_path, dockerfile_name)
        return Dockerfile.load_from_file_path(dockerfile_path)

    @staticmethod
    def load_from_file_path(dockerfile_path):
        if not os.path.isfile(dockerfile_path):
            raise Exception("Dockerfile not found at %s" % dockerfile_path)
        with open(dockerfile_path, 'r') as dockerfile:
            context = dockerfile.read()
            logging.debug("Read dockerfile from: %s", dockerfile_path)
        dockerfile = Dockerfile._parse(context)
        dockerfile.path = dockerfile_path
        return dockerfile

    @staticmethod
    def _parse(context):
        dockerfile = Dockerfile()

        dockerfile.physical_lines = context.splitlines()
        dockerfile.logical_lines = LogicalLineExtractor.parse_dockerfile(context)
        dockerfile.instructions = Dockerfile._create_instructions_from_logical_lines(dockerfile.logical_lines)
        dockerfile.stages = Dockerfile._set_stage_names_from_instructions(dockerfile.instructions)

        logging.debug("Dockerfile instructions successfully parsed: %s", dockerfile.instructions)

        return dockerfile

    @staticmethod
    def _create_instructions_from_logical_lines(logical_lines):
        instructions = list()
        for logical_line, according_physical_line in logical_lines:
            keyword, argument = logical_line.split(' ', 1)
            if keyword in Keywords.list:
                instruction = InstructionFactory.create_from_keyword(
                    keyword, argument, according_physical_line
                )
                instructions.append(instruction)
            else:
                raise Exception("Unknown instruction in Dockerfile: %s" % keyword)
        return instructions

    @staticmethod
    def _set_stage_names_from_instructions(instructions):
        stages = list()
        stage_index = -1
        stage = None
        for instruction in instructions:
            if instruction.get_type() == Keywords.FROM:
                stage_index += 1
                if instruction.stage_name:
                    stage = instruction.stage_name
                else:
                    stage = stage_index
                stages.append(stage)
            elif stage is None:
                logging.debug("Dockerfile did not start with a FROM instruction, stage -1 exists")
                stage = stage_index
                stages.append(stage_index)
            instruction.stage = stage
        return stages

    def lint(self, exit_on_errors, exclude):
        DockerfileLint(self, exit_on_errors, exclude).lint()

    def get_physical_lines(self):
        return self.physical_lines

    def get_last_stage(self):
        return self.stages[-1]

    def get_instructions(self, stage=None):
        instructions = list()
        for instruction in self.instructions:
            if stage is None or instruction.stage == stage:
                instructions.append(instruction)
        return instructions

    def get_instructions_of_type(self, instruction_type, stage=None):
        instructions = list()
        for instruction in self.get_instructions(stage=stage):
            if instruction.get_type() == instruction_type:
                instructions.append(instruction)
        return instructions

    def get_first_instruction_of_type(self, instruction_type, stage=None):
        for instruction in self.get_instructions(stage=stage):
            if instruction.get_type() == instruction_type:
                return instruction
        return None

    def get_maintainer_labels(self, ignore_case, stage=None):
        instructions = list()
        for instruction in self.get_instructions(stage=stage):
            if instruction.get_type() == Keywords.LABEL and instruction.contains("maintainer", ignore_case):
                instructions.append(instruction)
        return instructions

    def get_last_index_of(self, instruction_type, stage=None):
        last_index = -1
        for index, instruction in enumerate(self.instructions):
            if stage is None or instruction.stage == stage:
                if instruction.get_type() == instruction_type:
                    last_index = index
        return last_index

    def get_instruction_count(self, stage=None):
        return len(self.get_instructions(stage=stage))

    def contains_arg_with_name(self, name):
        """Returns true if arg is part of one of all instructions"""
        return name in set(instruction.name for instruction in self.get_instructions_of_type(Keywords.ARG))

    def __str__(self):
        return self.path if self.path else Dockerfile.dockerfile + " without path"
