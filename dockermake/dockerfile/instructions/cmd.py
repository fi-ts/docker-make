from dockermake.dockerfile.instructions.exec_form_base import ExecFormBase


class Cmd(ExecFormBase):
    def build_grammar(self):
        return self._exec_form_grammar()
