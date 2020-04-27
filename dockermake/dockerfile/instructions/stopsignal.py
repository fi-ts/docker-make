from dockermake.dockerfile.instructions.instruction_base import InstructionBase


class StopSignal(InstructionBase):
    def build_grammar(self):
        grammar = self.pp_word().setResultsName("stop_signal")

        return grammar
