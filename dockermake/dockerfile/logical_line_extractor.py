import pyparsing as pp

pp.ParserElement.enablePackrat()


class LogicalLineExtractor:
    DEFAULT_WHITESPACE = ' \t'
    BACKSLASH = '\\'
    HASH_MARK = '#'
    UNICODE_PRINTABLES = pp.printables  # pp.pyparsing_unicode.printables
    # STANDARD_CHARS = UNICODE_PRINTABLES.replace(BACKSLASH, '').replace(HASH_MARK, '')

    EOL = pp.LineEnd().suppress()
    SOL = pp.LineStart().leaveWhitespace()
    COMMENT = (HASH_MARK + pp.restOfLine).suppress()
    CONTINUATION = (pp.Literal(BACKSLASH).leaveWhitespace() + EOL).suppress()
    BLANKLINE = SOL + pp.LineEnd() | SOL + COMMENT + pp.LineEnd()

    @classmethod
    def parse_dockerfile(cls, context):
        """
        Parses the logical lines of a Dockerfile with pyparse. Returns tuples of
        tokens and physical line numbers.
        """
        parser = cls._parser()

        logical_lines = list()

        for line in parser.parseString(context):
            if line:
                logical_lines.append(line)

        return logical_lines

    @classmethod
    def _parser(cls):
        # Exclude newlines from the default whitespace characters
        # We need to deal with them manually
        pp.ParserElement.setDefaultWhitespaceChars(cls.DEFAULT_WHITESPACE)

        line = cls._line()
        body = pp.OneOrMore(line)

        parser = body + pp.StringEnd()
        parser.ignore(cls.BLANKLINE)
        parser.ignore(cls.COMMENT)

        return parser

    @classmethod
    def _line(cls):
        text = cls._free_form_text()

        physical_line = text + cls.EOL
        physical_line.setParseAction(
            lambda origString, loc, tokens: (tokens[0][0].rstrip(), pp.lineno(loc, origString))
        )
        logical_line = pp.OneOrMore(text + cls.CONTINUATION) + physical_line
        logical_line.setParseAction(
            lambda origString, loc, tokens: (''.join([x[0].lstrip() for x in tokens]), pp.lineno(loc, origString))
        )

        line = physical_line | logical_line | cls.EOL

        return line

    @classmethod
    def _free_form_text(cls):
        # Free-form text includes internal whitespace, but not leading or trailing
        text = pp.OneOrMore(pp.White(cls.DEFAULT_WHITESPACE) |
                            pp.QuotedString("'", multiline=False, escChar="\\", unquoteResults=False) |
                            pp.QuotedString('"', multiline=False, escChar="\\", unquoteResults=False) |
                            pp.Word(cls.UNICODE_PRINTABLES, excludeChars=cls.HASH_MARK + cls.BACKSLASH) |
                            cls._escape_codes())
        text.setParseAction(lambda origString, loc, tokens: (''.join(tokens), pp.lineno(loc, origString)))
        return text

    @classmethod
    def _escape_codes(cls):
        escaped_hash = pp.Literal(cls.BACKSLASH + cls.HASH_MARK)
        escaped_backslash = pp.Literal(cls.BACKSLASH + cls.BACKSLASH)
        return (cls.BACKSLASH + pp.Word(cls.UNICODE_PRINTABLES, exact=1)) | escaped_hash | escaped_backslash
