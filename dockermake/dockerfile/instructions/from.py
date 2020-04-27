import pyparsing as pp

from dockermake.dockerfile.instructions.instruction_base import InstructionBase


class From(InstructionBase):
    def build_grammar(self):
        def flatten(tokens):
            return tokens[0]

        def add_back_trailing_slash(tokens):
            if tokens:
                tokens[0] += "/"
            return tokens

        registry = pp.Optional(self.pp_word(without="/").setResultsName("registry") + "/")
        username = pp.Optional(
            pp.OneOrMore(self.pp_word(without="/") + pp.Suppress("/")).addParseAction("/".join).setResultsName(
                "username")).addParseAction(add_back_trailing_slash)
        image = self.pp_word(without="/:").setResultsName("image")
        tag = pp.Optional(":" + self.pp_word().setResultsName("tag"))

        full_image = pp.Combine(registry + username + image + tag).setResultsName("full_image_name")
        full_image.addParseAction(flatten)

        stage_name = pp.Optional(pp.CaselessLiteral("as") + self.pp_word().setResultsName("stage_name"))

        grammar = full_image + stage_name

        return grammar
