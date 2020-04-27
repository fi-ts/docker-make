import logging
import json
import re


class PosixStyleExpander:
    @classmethod
    def expand(cls, config, replacement_dict):
        """
        Expands posix style variables in a json convert-able data structure with values in a replacement
        dictionary.
        """
        context = json.dumps(config)

        for string in re.findall(r'\${[^}]+}|\$\w+', context):
            var, default, required = cls._extract_posix_variable_parts(string)

            replacement = replacement_dict.get(var, default)

            if not replacement:
                if required:
                    raise Exception("Environment variable '%s' was required but had no value." % var)
                logging.warning("A variable was not consumed and defaulted to an empty string: %s", var)
                replacement = ""

            context = context.replace(string, replacement)

        logging.debug("Expanded config: %s", context)

        return json.loads(context, strict=False)

    @classmethod
    def _extract_posix_variable_parts(cls, string):
        string = cls._enforce_braces(string)  # for simpler handling of the string
        for splitter in [":-", ":=", "-", None]:
            var, default, required = cls._split_var_from_default(string, splitter)
            if var:
                break
        return var, default, required

    @staticmethod
    def _enforce_braces(string):
        if string.startswith('$') and not string.startswith('${'):
            string = "${" + string[1:] + "}"
        return string

    @classmethod
    def _split_var_from_default(cls, string, splitter):
        var = None
        default = None
        required = False
        if not splitter:
            required = string[-2] == "?"
            if required:
                var = string[2:-2]
            else:
                var = string[2:-1]
        elif len(string.split(splitter)) > 1:
            parts = string.split(splitter)
            var = parts[0][2:]
            default = parts[1][0:-1]
        return var, default, required
