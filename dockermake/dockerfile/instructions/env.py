from dockermake.dockerfile.instructions.assignments_form_base import AssignmentsFormBase


class Env(AssignmentsFormBase):
    def build_grammar(self):
        return self._assignments_form_grammar()
