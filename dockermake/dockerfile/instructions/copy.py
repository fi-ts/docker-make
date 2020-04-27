import pyparsing as pp

from dockermake.dockerfile.instructions.instruction_base import InstructionBase


class Copy(InstructionBase):
    def build_grammar(self):
        chown = pp.Combine(self.pp_word(without=":") + ":" + self.pp_word())
        chown_clause = self.pp_optional_parameter("chown", chown, None)

        from_stage_clause = self.pp_optional_parameter("from", self.pp_word(), None)

        options = chown_clause & from_stage_clause

        exec_form = self._exec_form_grammar()
        shell_form = self._shell_form_grammar()

        grammar = options + (exec_form ^ shell_form)

        return grammar

    @staticmethod
    def _shell_form_grammar():
        path = InstructionBase.pp_path()
        src = pp.Group(pp.OneOrMore(path + ~pp.FollowedBy(pp.StringEnd()))).setResultsName("src")
        dest = path.setResultsName("dest")
        grammar = src + dest
        return grammar

    @staticmethod
    def _exec_form_grammar():
        start = "["
        end = "]"
        src = InstructionBase.pp_quoted(unquote=True).setResultsName("src", listAllMatches=True)
        following_src = pp.ZeroOrMore("," + src + ~pp.FollowedBy(end))
        dest = "," + InstructionBase.pp_quoted(unquote=True).setResultsName("dest")
        grammar = start + src + following_src + dest + end
        return grammar
