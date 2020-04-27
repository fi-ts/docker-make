import pyparsing as pp

from dockermake.dockerfile.instructions.instruction_base import InstructionBase


class Healthcheck(InstructionBase):
    def build_grammar(self):
        interval_clause = self.pp_optional_parameter("interval", self.pp_word(), "30s")
        timeout_clause = self.pp_optional_parameter("timeout", self.pp_word(), "30s")
        start_period_clause = self.pp_optional_parameter("start_period", self.pp_word(), "0s")
        retries_clause = self.pp_optional_parameter("retries", self.pp_word(), "3")

        options = interval_clause & timeout_clause & start_period_clause & retries_clause

        healthcheck_command = "CMD " + pp.restOfLine.setResultsName("cmd")

        grammar = options + ("NONE" ^ healthcheck_command)

        return grammar
