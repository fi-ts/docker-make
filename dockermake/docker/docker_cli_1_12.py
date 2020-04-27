from dockermake.docker.docker_cli_base import DockerCliBase
from dockermake.docker.command_base import CommandBase


class DockerCli112(DockerCliBase):
    DOCKER_CLI_VERSION = "1.12"

    @classmethod
    def build(cls, path, **kwargs):
        return cls.BuildCommand(path, **kwargs).run()

    @classmethod
    def docker_cli_version(cls):
        return cls.DOCKER_CLI_VERSION

    @classmethod
    def inspect(cls, name, **kwargs):
        return cls.InspectCommand(name, **kwargs).run()

    @classmethod
    def images(cls, **kwargs):
        out, _, _ = cls.ImagesCommand(**kwargs).run()
        images = set()
        if out:
            for line in out.splitlines():
                image = line.strip()
                if not image:
                    continue
                images.add(image)
        return list(images)

    @classmethod
    def login(cls, server, **kwargs):
        password = kwargs.get("password")
        if password:
            kwargs["stdin_feed"] = password
        return cls.LoginCommand(server, **kwargs).run()

    @classmethod
    def pull(cls, image, **kwargs):
        return cls.PullCommand(image, **kwargs).run()

    @classmethod
    def push(cls, image, **kwargs):
        return cls.PushCommand(image, **kwargs).run()

    @classmethod
    def remove_images(cls, image, **kwargs):
        return cls.RemoveImagesCommand(image, **kwargs).run()

    @classmethod
    def tag(cls, source_image, target_image, **kwargs):
        return cls.TagCommand(source_image, target_image, **kwargs).run()

    # pylint: disable=too-many-instance-attributes
    class BuildCommand(CommandBase):
        BUILD = "build"

        def __init__(self, path, **kwargs):
            self.path = path
            self.build_args = kwargs.pop("build_args", [])
            self.labels = kwargs.pop("labels", [])
            self.pull = kwargs.pop("pull", False)
            self.remove = kwargs.pop("remove", False)
            self.tags = kwargs.pop("tags", [])
            self.quiet = kwargs.pop("quiet", False)
            self.file = kwargs.pop("file", None)
            self.no_cache = kwargs.pop("no_cache", False)
            self.target = kwargs.pop("target", None)
            super(DockerCli112.BuildCommand, self).__init__(**kwargs)

        def _build_command(self):
            parts = self._base()
            parts.append(self.BUILD)

            for build_arg in self.build_args:
                parts.append("--build-arg")
                parts.append(build_arg)
            for label in self.labels:
                parts.append("--label")
                parts.append(label)
            if self.file:
                parts.append("--file")
                parts.append(self.file)
            if self.no_cache:
                parts.append("--no-cache")
            if self.pull:
                parts.append("--pull")
            if self.remove:
                parts.append("--rm")
            for tag in self.tags:
                parts.append("--tag")
                parts.append(tag)
            if self.quiet:
                parts.append("--quiet")
            if self.target:
                parts.append("--target")
                parts.append(self.target)

            parts.append(self.path)

            return parts

    class InspectCommand(CommandBase):
        INSPECT = "inspect"

        def __init__(self, name, **kwargs):
            self.name = name
            self.output_format = kwargs.pop("output_format", None)
            self.size = kwargs.pop("size", False)
            super(DockerCli112.InspectCommand, self).__init__(**kwargs)

        def _build_command(self):
            parts = self._base()
            parts.append(self.INSPECT)

            if self.output_format:
                parts.append("--format")
                parts.append(self.output_format)
            if self.size:
                parts.append("--size")

            parts.append(self.name)

            return parts

    class ImagesCommand(CommandBase):
        IMAGES = "images"

        def __init__(self, **kwargs):
            self.image = kwargs.pop("image", None)
            self.all_images = kwargs.pop("all_images", False)
            self.digests = kwargs.pop("digests", False)
            self.image_filter = kwargs.pop("image_filter", None)
            self.output_format = kwargs.pop("output_format", None)
            self.no_trunc = kwargs.pop("no_trunc", False)
            self.quiet = kwargs.pop("quiet", False)
            super(DockerCli112.ImagesCommand, self).__init__(**kwargs)

        def _build_command(self):
            parts = self._base()
            parts.append(self.IMAGES)

            if self.all_images:
                parts.append("--all")
            if self.digests:
                parts.append("--digests")
            if self.image_filter:
                parts.append("--filter")
                parts.append(self.image_filter)
            if self.output_format:
                parts.append("--format")
                parts.append(self.output_format)
            if self.no_trunc:
                parts.append("--no-trunc")
            if self.quiet:
                parts.append("--quiet")

            if self.image:
                parts.append(self.image)

            return parts

    class LoginCommand(CommandBase):
        LOGIN = "login"

        def __init__(self, server, **kwargs):
            self.server = server
            self.user = kwargs.pop("user", None)
            self.password = kwargs.pop("password", None)
            super(DockerCli112.LoginCommand, self).__init__(**kwargs)

        def _build_command(self):
            parts = self._base()
            parts.append(self.LOGIN)

            if self.user:
                parts.append("--username")
                parts.append(self.user)
            if self.password:
                parts.append("--password-stdin")

            parts.append(self.server)

            return parts

    class PullCommand(CommandBase):
        PULL = "pull"

        def __init__(self, image, **kwargs):
            self.image = image
            self.all_tags = kwargs.pop("all_tags", False)
            self.disable_content_trust = kwargs.pop("disable_content_trust", False)
            super(DockerCli112.PullCommand, self).__init__(**kwargs)

        def _build_command(self):
            parts = self._base()
            parts.append(self.PULL)

            if self.all_tags:
                parts.append("--all-tags")
            if self.disable_content_trust:
                parts.append("--disable-content-trust")

            parts.append(self.image)

            return parts

    class PushCommand(CommandBase):
        PUSH = "push"

        def __init__(self, image, **kwargs):
            self.image = image
            self.disable_content_trust = kwargs.pop("disable_content_trust", False)
            super(DockerCli112.PushCommand, self).__init__(**kwargs)

        def _build_command(self):
            parts = self._base()
            parts.append(self.PUSH)

            if self.disable_content_trust:
                parts.append("--disable-content-trust")

            parts.append(self.image)

            return parts

    class RemoveImagesCommand(CommandBase):
        REMOVE_IMAGES = "rmi"

        def __init__(self, image, **kwargs):
            self.image = image
            self.force = kwargs.pop("force", False)
            self.no_prune = kwargs.pop("no_prune", False)
            super(DockerCli112.RemoveImagesCommand, self).__init__(**kwargs)

        def _build_command(self):
            parts = self._base()
            parts.append(self.REMOVE_IMAGES)

            if self.force:
                parts.append("--force")
            if self.no_prune:
                parts.append("--no-prune")

            if isinstance(self.image, list):
                parts += self.image
            else:
                parts.append(self.image)

            return parts

    class TagCommand(CommandBase):
        TAG = "tag"

        def __init__(self, source_image, target_image, **kwargs):
            self.source_image = source_image
            self.target_image = target_image
            super(DockerCli112.TagCommand, self).__init__(**kwargs)

        def _build_command(self):
            parts = self._base()
            parts.append(self.TAG)

            parts.append(self.source_image)
            parts.append(self.target_image)

            return parts
