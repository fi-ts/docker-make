import json
import logging
import os
import subprocess
import sys

from dockermake.utils import display


class System:
    OMITTED_CMD = "*** command hidden as sensible information are contained ***"

    @classmethod
    def run_commands(cls, cmds, **kwargs):
        for cmd in cmds:
            cls.run_command(cmd, **kwargs)

    @staticmethod
    # pylint: disable-msg=R0913
    def run_command(cmd, shell=False, dry_run=False, cwd=None, fail_on_bad_return_code=True,
                    with_continuous_output=False, omit_printing_output=False, stdin_feed=None):

        cmd_for_printing = System._get_cmd_for_printing(cmd, omit_printing_output)

        if dry_run:
            display.info("[DRY] Would execute command: %s" % cmd_for_printing)
            return "", "", 0

        logging.debug("Executing command: %s", cmd_for_printing)
        out, err, return_code = System._run_command(cmd, shell, cwd, with_continuous_output, stdin_feed)

        if fail_on_bad_return_code and return_code != 0:
            if err:
                raise Exception("Command returned with exit code %s: %s, stderr: %s" %
                                (return_code, cmd_for_printing, err))
            raise Exception("Command returned with exit code %s: %s" % (return_code, cmd_for_printing))

        return out, err, return_code

    @staticmethod
    def _get_cmd_for_printing(cmd, omit_printing_output):
        cmd_for_printing = System.OMITTED_CMD if omit_printing_output else cmd
        if isinstance(cmd_for_printing, list):
            return " ".join(cmd_for_printing)
        return cmd_for_printing

    @staticmethod
    def _run_command(cmd, shell, cwd, with_continuous_output, stdin_feed):
        if with_continuous_output:
            return System._with_continuous_output(cmd, shell=shell, cwd=cwd)
        return System._without_continuous_output(cmd, shell=shell, cwd=cwd, stdin_feed=stdin_feed)

    @staticmethod
    def _with_continuous_output(cmd, shell, cwd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=shell, bufsize=1, cwd=cwd, env=os.environ,
                                   encoding='UTF-8')
        err = None
        out = ""
        while True:
            partial_out = process.stdout.readline().strip()
            if partial_out == "" and process.poll() is not None:
                break
            if partial_out:
                out += partial_out
                display.info(partial_out)
                sys.stdout.flush()
        return_code = process.poll()
        out, err = System._clean_outputs(out, err)
        return out, err, return_code

    @staticmethod
    def _without_continuous_output(cmd, shell, cwd, stdin_feed):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                   shell=shell, cwd=cwd, env=os.environ, encoding='UTF-8')
        out, err = process.communicate(input=stdin_feed)
        return_code = process.returncode
        out, err = System._clean_outputs(out, err)
        logging.debug("Command output was: %s", out)
        return out, err, return_code

    @staticmethod
    def _clean_outputs(out, err):
        if out is None:
            out = ""
        if err is None:
            err = ""
        if out:
            out = out.strip()
        if err:
            err = err.strip()
        return out, err


def dockerfile_keyword(**enums):
    reverse = dict((value, key) for key, value in list(enums.items()))
    enums["list"] = sorted(enums.keys())
    enums["mapping"] = enums
    enums["reverse_mapping"] = reverse
    return type("DockerfileKeyword", (), enums)


def enum(*sequential, **named):
    enums = dict(list(zip(sequential, list(range(len(sequential))))), **named)
    return type('Enum', (), enums)


def load_json(path):
    with open(path, 'r') as stream:
        data = stream.read()
    return json.loads(data)
