import argparse
import logging
import sys
import configargparse
from dockermake.constants import Constants
from dockermake.version import VERSION
from dockermake.make import Make
from dockermake.lint.linting_exception import LintingException
from dockermake.utils import display


class ExtendAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest) or []
        items.extend(values)
        setattr(namespace, self.dest, items)


def main():
    parser, args = parse(sys.argv[1:])

    logging.basicConfig(format=args.log_format, level=args.log_level)

    logging.debug(args)
    logging.debug(parser.format_values())

    make = Make(args)

    try:
        make.run()
    except KeyboardInterrupt:
        display.error("User interrupted execution")
        sys.exit(99)
    except LintingException as exception:
        display.error("Error: " + str(exception))
        sys.exit(2)
    # for hiding the stack trace from the user, it is tolerable to catch Exception once in the project
    except Exception as exception:  # pylint: disable=broad-except
        if args.log_level == "DEBUG":
            raise
        display.error("Error: " + str(exception))
        sys.exit(1)

    sys.exit(0)


def parse(args):
    parser = configargparse.ArgParser(
        auto_env_var_prefix="DOCKER_MAKE_",
        default_config_files=Constants.DEFAULT_CONFIG_FILE_PATHS,
        config_file_parser_class=configargparse.YAMLConfigFileParser,
        prog=Constants.DOCKER_MAKE_BASE_NAME,
        description="Build containers with tags and different build-args with Docker."
    )
    parser.add_argument("-c", "--config-file", type=str, is_config_file=True,
                        help="path to a docker-make config file")
    parser.add_argument("--log-level", type=str, default=Constants.DEFAULT_LOG_LEVEL,
                        help="defines the python logger's log level")
    parser.add_argument("--log-format", type=str, default=Constants.DEFAULT_LOG_FORMAT,
                        help="defines the python logger's log format")
    parser.add_argument("--show-sensible-console-output", action='store_true',
                        default=Constants.DEFAULT_SHOW_SENSIBLE_CONSOLE_OUTPUT,
                        help="Prevents output with sensible information (e.g. credentials) in console output")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s " + VERSION,
                        env_var="DOCKER_MAKE_SHOW_VERSION")
    parser.add_argument("-B", "--show-builds", action='store_true', default=False,
                        help="show all builds and exit")
    parser.add_argument("--show-linting-rules", action='store_true', default=False,
                        help="show all linting rules and exit")
    parser.add_argument("-x", "--exclude-linting-rules", action="append",
                        help="excludes the given linting rules (comma-separated, multiple are appended)")
    parser.add_argument("-b", "--build-only", nargs="+", dest="build_only_names",
                        help="build only given builds")
    parser.add_argument("-f", "--file", type=str, default=None, help="specify an alternative docker-make file")
    parser.add_argument("--dockerfile", type=str, default=Constants.DEFAULT_DOCKERFILE,
                        help="specify an alternative name for Dockerfile in working directory")
    parser.add_argument("--registries-file", type=str, default=Constants.DEFAULT_REGISTRIES_FILE_PATH,
                        help="specify an alternative path for registries.yaml")
    parser.add_argument("--push-only-to-defined-registries", action='store_true',
                        default=Constants.DEFAULT_PUSH_ONLY_TO_DEFINED_REGISTRIES,
                        help="pushes images only to registries defined in registries.yaml")
    parser.add_argument("--push-only-to-specific-git-projects", action='store_true',
                        default=Constants.DEFAULT_PUSH_ONLY_TO_SPECIFIC_GIT_PROJECTS,
                        help="pushes images only to registry git projects defined in registries.yaml")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--lint", action='store_const', dest='linting', const='exit_on_errors',
                       help="lint given Dockerfile, fail on errors.")
    group.add_argument("-L", "--Lint", action='store_const', dest='linting', const='proceed_on_errors',
                       help="lint given Dockerfile, proceed on errors.", env_var="DOCKER_MAKE_LINT_AND_PROCEED")
    group.add_argument("--no-lint", action='store_const', dest='linting', const=None,
                       help="no linting of the Dockerfile.")
    parser.set_defaults(linting='exit_on_errors')
    parser.add_argument("--only-lint", action='store_true', default=False,
                        help="only lint and exit.")
    parser.add_argument("-n", "--no-push", action='store_true', default=False,
                        help="only build the images but do not push the images to the registry-host")
    parser.add_argument("-N", "--no-pull", action='store_true', default=False,
                        help="during build do not pull the parent image from the registry-host")
    parser.add_argument("--no-cache", action='store_true', default=False,
                        help="do not use cache when building the image")
    parser.add_argument("--target", type=str,
                        help="set the target build stage to build")
    parser.add_argument("--skip-registry-auth", action='store_true', default=False,
                        help="skips registry authentication and just tries to push to the registry defined")
    parser.add_argument("-d", "--dry-run", action='store_true', default=False,
                        help="only show what docker-make would do but do not execute commands with an impact")
    parser.add_argument("-p", "--purge", action='store_true', default=False,
                        help="""purge all previous created images __before__ running the actual build.
                        Purge forcefully removes the docker images.
                        IMPORTANT: This is not recommended for containers which have children""")
    parser.add_argument("-s", "--summary", action='store_true', default=False,
                        help="print a markdown formatted summary of this build, which can be added to your "
                             "documentation")
    parser.add_argument("--create-parent-label", action='store_true', default=Constants.DEFAULT_CREATE_PARENT_LABEL,
                        help="creates a label with the image parents of the resulting docker image")
    parser.add_argument("--parent-label-name", type=str, default=Constants.DEFAULT_PARENT_LABEL_NAME,
                        help="the parent build urls label name")
    parser.add_argument("--create-git-remote-url-label", action='store_true',
                        default=Constants.DEFAULT_CREATE_GIT_REMOTE_URL_LABEL,
                        help="creates a label with the git remote url when pushing from git folder")
    parser.add_argument("--git-remote-url-label-name", type=str, default=Constants.DEFAULT_GIT_REMOTE_URL_LABEL_NAME,
                        help="the git remote url label name")
    parser.add_argument("--create-git-sha1-label", action='store_true',
                        default=Constants.DEFAULT_CREATE_GIT_SHA1_LABEL,
                        help="creates a label with the git hash when pushing from git folder")
    parser.add_argument("--git-sha1-label-name", type=str, default=Constants.DEFAULT_GIT_SHA1_LABEL_NAME,
                        help="the git sha1 label name")
    parser.add_argument("--create-built-from-scratch-label", action='store_true',
                        default=Constants.DEFAULT_BUILT_FROM_SCRATCH_LABEL_NAME,
                        help="creates a label that indicates whether the container was built from scratch or not")
    parser.add_argument("--built-from-scratch-label-name", type=str,
                        default=Constants.DEFAULT_BUILT_FROM_SCRATCH_LABEL_NAME,
                        help="the built from scratch label name")
    parser.add_argument("-w", "--work-dir", type=str, default=Constants.DEFAULT_WORK_DIR,
                        help="change the working directory (defaults to %s)" % Constants.DEFAULT_WORK_DIR)
    parser.register('action', 'extend', ExtendAction)
    parser.add_argument("--label", nargs="*", action="extend", default=[], dest="labels",
                        help="labels attached to the resulting container images")
    parser.add_argument("--build-arg", nargs="*", action="extend", default=[], dest="docker_build_args",
                        help="any valid Docker build parameter like \"--build-arg XYZ=abc\"")

    return parser, parser.parse_args(args)
