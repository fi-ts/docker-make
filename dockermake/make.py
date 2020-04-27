import os
import logging
import json

from mock import patch

from dockermake.constants import Constants
from dockermake.dockerfile.dockerfile import Dockerfile
from dockermake.dockerfile.instructions import Keywords
from dockermake.config.loader import ConfigLoader
from dockermake.docker.docker_cli_factory import DockerCliFactory
from dockermake.git import check_if_git_is_installed
from dockermake.git.git import get_gitsha1_hash_of_head, get_git_remote_origin_url
from dockermake.registries.registries import Registries
from dockermake.utils.helpers import System
from dockermake.utils.summary_printer import SummaryPrinter
from dockermake.utils import display


class Make:
    def __init__(self, args):
        self.args = args
        Dockerfile.dockerfile = self.args.dockerfile
        self.dockerfile = None
        self.config = None
        self.docker_cli = DockerCliFactory.create()
        self.registries = Registries()
        self.registries.load(self.args)

    def run(self):
        if self.args.show_linting_rules:
            SummaryPrinter.print_rule_summary()
            return

        self.dockerfile = Dockerfile.load(self.args.work_dir, self.args.dockerfile)

        if self.args.only_lint:
            self.dockerfile.lint(exit_on_errors=True, exclude=self.args.exclude_linting_rules)
            return
        self._lint()

        self.check_prerequisites()
        self.load()

        if self.args.show_builds:
            self.config.print_builds()
            return

        if self.args.build_only_names:
            self.config.narrow_down_builds_by_names(self.args.build_only_names)

        self._make()

    @staticmethod
    def check_prerequisites():
        check_if_git_is_installed()

    def load(self):
        self.config = ConfigLoader.load(self.args.work_dir, additional_build_args=self.args.docker_build_args,
                                        alternative_file=self.args.file)
        self._prepare_config()
        self._validate_config()

    def _prepare_config(self):
        self.config.add_metadata_to_config(self.dockerfile)
        self.config.expand()

    def _validate_config(self):
        self.config.validate(self.dockerfile)

    def _lint(self):
        if self.args.linting is None:
            return

        if self.args.linting == 'exit_on_errors':
            self.dockerfile.lint(exit_on_errors=True, exclude=self.args.exclude_linting_rules)

        if self.args.linting == 'proceed_on_errors':
            self.dockerfile.lint(exit_on_errors=False, exclude=self.args.exclude_linting_rules)

    def _make(self):
        self._run_before_commands()

        if self.args.purge:
            self._purge()

        if not self.args.skip_registry_auth:
            self._run_registry_auth_commands()

        build_summary = list()
        for build in self.config.get_builds():
            self._run_before_build_commands(build)
            summary_part = self._run_docker_build_and_push_commands(build)
            build_summary.append(summary_part)
            self._run_after_build_commands(build)

        self._run_after_commands()

        SummaryPrinter.print_tag_list(build_summary)
        if self.args.summary:
            SummaryPrinter.print_full_build_summary(build_summary)

    def _run_before_commands(self):
        self._run_commands(self.config.get_before_commands(), "before commands")

    def _run_commands(self, commands, name):
        logging.info("Running %s", name)
        if commands:
            System.run_commands(commands, dry_run=self.args.dry_run, with_continuous_output=True,
                                cwd=self.args.work_dir, shell=True)
            logging.info("Finished running %s", name)
        else:
            logging.info("No commands given, continuing...")

    def _run_after_commands(self):
        self._run_commands(self.config.get_after_commands(), "after commands")

    def _purge(self):
        image = self.config.get_image_name()
        logging.info("Retrieving images to purge")
        images_to_purge = self.docker_cli.images(image=image, quiet=True)

        if images_to_purge:
            logging.info("Running purge command")
            self.docker_cli.remove_images(images_to_purge, force=True, dry_run=self.args.dry_run,
                                          with_continuous_output=True)
        else:
            logging.info("No images to purge")

    def _run_registry_auth_commands(self):
        registry_name = self.config.get_registry_host()

        user, password = self.registries.get_registry_authentication(registry_name)
        if user and password:
            logging.info("Running registry auth commands")
            self.docker_cli.login(registry_name, user=user, password=password, dry_run=self.args.dry_run,
                                  with_continuous_output=False, omit_printing_output=self.omit_sensible_output())
        else:
            logging.info("Skipping authentication, no registry auth credentials provided")

    def _run_before_build_commands(self, build):
        self._run_commands(self.config.get_before_build_commands(build), "before build commands")

    def _run_docker_build_and_push_commands(self, build):
        summary_part = build.copy()

        summary_part["build-args"] = build_args = self._gather_build_args(build)
        summary_part["build-labels"] = build_labels = self._gather_build_labels(build)
        summary_part["build-tags"] = image_tags = self._gather_image_tags(build)

        logging.info("Running docker build command")
        self.docker_cli.build(
            self.args.work_dir,
            build_args=build_args,
            labels=build_labels,
            no_cache=self.args.no_cache,
            target=self.args.target,
            remove=True,
            file=os.path.join(self.args.work_dir, self.args.dockerfile),
            tags=image_tags,
            pull=self.pull(),
            dry_run=self.args.dry_run,
            with_continuous_output=True
        )

        if self.push():
            registry_name = self.config.get_registry_host()
            self.registries.check_allowed_to_push(registry_name)
            if image_tags:
                logging.info("Running docker push commands")
                for tag in image_tags:
                    self.docker_cli.push(tag, dry_run=self.args.dry_run, with_continuous_output=True)

                logging.debug("Inspecting image for summary")
                inspect_output = self.inspect_image(image_tags[0], output_format="{{ json . }}")
                for repo_digest in inspect_output.get("RepoDigests", []):
                    summary_part["digest"] = repo_digest.split("@")[-1]
                    break
                props = dict(RepoDigests=inspect_output.get("RepoDigests"),
                             RepoTags=inspect_output.get("RepoTags"),
                             Size="%.2f MB" % (inspect_output.get("Size", 0) / 1024.0 / 1024.0),
                             ID=inspect_output.get("Id"),
                             Created=inspect_output.get("Created"))
                summary_part["image-properties"] = props

            else:
                logging.info("No images to push")
        else:
            logging.info("Skipping docker push command due to --no-push option")

        return summary_part

    def _run_after_build_commands(self, build):
        self._run_commands(self.config.get_after_build_commands(build), "after build commands")

    def _gather_build_args(self, build):
        return self.config.get_merged_build_args(build)

    def _gather_build_labels(self, build):
        build_labels = self.config.get_merged_build_labels(build)
        build_labels += self.create_git_labels()
        build_labels += self.args.labels

        try:
            base_image = self._get_base_image(self._gather_build_args(build))
        except Exception as exception:
            raise Exception("Error determining base image", exception)

        if self.args.create_parent_label:
            build_labels += self.create_parent_label(base_image)
        if self.args.create_built_from_scratch_label:
            build_labels += self.create_built_from_scratch_label(base_image)
        return build_labels

    def _gather_image_tags(self, build):
        image_tags = list()

        default_build = self.config.get_default_build()
        if default_build == build:
            image_tag = self.config.get_image_name(tag=get_gitsha1_hash_of_head())
            image_tags.append(image_tag)

        for build_tag in self.config.get_build_tags(build):
            image_tag = self.config.get_image_name(tag=build_tag)
            image_tags.append(image_tag)

        return image_tags

    def pull(self):
        return not self.args.no_pull

    def push(self):
        return not self.args.no_push

    def omit_sensible_output(self):
        return not self.args.show_sensible_console_output

    def create_git_labels(self):
        labels = list()

        git_remote_url = get_git_remote_origin_url()
        if git_remote_url:
            labels.append(self.args.git_remote_url_label_name + "=" + git_remote_url)

        git_hash = get_gitsha1_hash_of_head()
        if git_hash:
            labels.append(self.args.git_sha1_label_name + "=" + git_hash)

        return labels

    def create_built_from_scratch_label(self, base_image):
        built_from_scratch = base_image == "scratch"

        return ["=".join([self.args.built_from_scratch_label_name + "=" + json.dumps(built_from_scratch)])]

    def create_parent_label(self, base_image):
        if Constants.CI_BUILD_URL is None:
            raise Exception(
                "No CI build URL found for adding to parent labels, please provide BUILD_URL in environment or "
                "disable building parent labels by setting DOCKER_MAKE_CREATE_PARENT_LABELS to false")

        if base_image == "scratch":
            # scratch images cannot be inspected
            inspect_labels = {self.args.parent_label_name: json.dumps([])}
        else:
            inspect_labels = self.inspect_image(base_image, output_format="{{ json .ContainerConfig.Labels }}")
            # a base image can also have no labels at all -> None
            if inspect_labels is None:
                inspect_labels = dict()

        parent_urls_string = inspect_labels.get(self.args.parent_label_name, "[]")

        try:
            parent_urls = json.loads(parent_urls_string)
        except ValueError as exception:
            # in older versions, parent urls were invalid json... this is a workaround
            if parent_urls_string.startswith("[") and parent_urls_string.endswith("]"):
                parent_urls = [url.strip() for url in parent_urls_string[1:-1].split(",") if url]
            else:
                raise Exception(
                    "Could not parse parent labels, invalid JSON: '%s', %s" % (parent_urls_string, exception))

        parent_urls.append(Constants.CI_BUILD_URL)

        return [self.args.parent_label_name + "=" + json.dumps(parent_urls)]

    def _get_base_image(self, build_args):
        base_image = self.dockerfile.get_first_instruction_of_type(
            Keywords.FROM, stage=self.dockerfile.get_last_stage()
        ).full_image_name

        if not base_image:
            raise Exception("Error: No FROM instruction in Dockerfile defined")

        # maybe ARG is used before the FROM instruction, we need to render the variables into the base image
        arg_instructions = []
        for instruction in self.dockerfile.get_instructions():
            if instruction.get_type() == Keywords.ARG:
                arg_instructions.append(instruction)
                continue
            break

        if arg_instructions:
            build_arg_map = dict()
            for build_arg in build_args:
                key, value = build_arg.split("=", 1)
                build_arg_map[key] = value

            replacement_dict = dict()

            for arg_instruction in arg_instructions:
                replacement_value = build_arg_map.get(arg_instruction.name, arg_instruction.default)
                if replacement_value is None:
                    continue
                replacement_dict[arg_instruction.name] = replacement_value

            with patch.dict(os.environ, replacement_dict):
                base_image = os.path.expandvars(base_image)

        return base_image

    def inspect_image(self, image, output_format):
        output, _, return_code = self.docker_cli.inspect(image, output_format=output_format,
                                                         dry_run=self.args.dry_run, fail_on_bad_return_code=False)
        if return_code != 0:
            logging.info(
                "Attempt to pull image %s from the registry to run inspect command")
            try:
                self._pull_docker_image(image)
            except Exception as exception:
                display.error("Pulling image to run inspect command failed")
                display.warn("Please make sure you do not modify the Dockerfile's FROM instruction "
                             "in before and after commands, use ARG before FROM instead")
                raise exception
            output, _, _ = self.docker_cli.inspect(image, output_format=output_format)

        return json.loads(output) if output else dict()

    def _pull_docker_image(self, image):
        if self.pull():
            logging.info("Pulling image")
            self.docker_cli.pull(image, dry_run=self.args.dry_run, with_continuous_output=True)
        else:
            logging.info("Skipping image pull due to no pull")
