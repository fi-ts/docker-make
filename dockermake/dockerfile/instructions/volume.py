from dockermake.dockerfile.instructions.exec_form_base import ExecFormBase


class Volume(ExecFormBase):
    def build_grammar(self):
        return self._exec_form_grammar()
