import unittest

from dockermake.dockerfile.dockerfile import Dockerfile
from dockermake.dockerfile.instructions import Keywords


class DockerfileTest(unittest.TestCase):
    def test_context_parse(self):
        context = """
        FROM centos
        ADD asdf asdf
        CMD ['bash']
        """
        df = Dockerfile._parse(context)
        instructions = df.instructions
        self.assertEqual(len(instructions), 3)
        self.assertEqual(instructions[0].argument, "centos")
        self.assertEqual(instructions[1].argument, "asdf asdf")
        self.assertEqual(instructions[2].argument, "['bash']")

    def test_keywords(self):
        expected = ['ADD', 'ARG', 'CMD', 'COPY', 'ENTRYPOINT', 'ENV', 'EXPOSE',
                    'FROM', 'HEALTHCHECK', 'LABEL', 'MAINTAINER', 'ONBUILD',
                    'RUN', 'SHELL', 'STOPSIGNAL', 'USER', 'VOLUME', 'WORKDIR']
        self.assertEqual(expected, Keywords.list)

    def test_copy_add_dockerfile(self):
        context = """
        FROM	centos:7.3
        LABEL	maintainer	Somebody <with@somemail.com>
        
        COPY	.	/go/src/github.com/docker/docker
        ADD		.	/
        ADD		null /
        COPY	nullfile /tmp
        ADD		[ "vimrc", "/tmp" ]
        COPY	[ "bashrc", "vimrc", "/tmp" ]
        ADD		[ "test file", "/tmp/test file" ]
        """

        df = Dockerfile._parse(context)
        instructions = df.instructions
        self.assertEqual(len(instructions), 9)
        self.assertEqual(instructions[0].full_image_name, "centos:7.3")
        self.assertEqual(instructions[1].assignments.get("maintainer", None), "Somebody <with@somemail.com>")
        self.assertEqual(instructions[2].src, ['.'])
        self.assertEqual(instructions[2].dest, '/go/src/github.com/docker/docker')
        self.assertEqual(instructions[3].src, ['.'])
        self.assertEqual(instructions[3].dest, '/')
        self.assertEqual(instructions[4].src, ['null'])
        self.assertEqual(instructions[4].dest, '/')
        self.assertEqual(instructions[5].src, ['nullfile'])
        self.assertEqual(instructions[5].dest, '/tmp')
        self.assertEqual(instructions[6].src, ['vimrc'])
        self.assertEqual(instructions[6].dest, '/tmp')
        self.assertEqual(instructions[7].src, ['bashrc', 'vimrc'])
        self.assertEqual(instructions[7].dest, '/tmp')
        self.assertEqual(instructions[8].src, ['test file'])
        self.assertEqual(instructions[8].dest, '/tmp/test file')

    def test_dockerfile_with_entrypoint(self):
        context = """
        FROM registry/alpine:1.2.3
        LABEL maintainer Some maintainer "some@maintainer.com"
        ENV GIT_HASH unknown
        RUN apk update
        RUN apk install some packages_${GIT_HASH}
        EXPOSE 42
        ENTRYPOINT [ "/usr/bin/some-server" ]
        """

        df = Dockerfile._parse(context)
        instructions = df.instructions
        self.assertEqual(len(instructions), 7)
        self.assertEqual(instructions[0].image, "alpine")
        self.assertEqual(instructions[0].registry, "registry")
        self.assertEqual(instructions[0].username, None)
        self.assertEqual(instructions[1].assignments.get("maintainer", None), 'Some maintainer "some@maintainer.com"')
        self.assertEqual(instructions[2].assignments.get("GIT_HASH", None), "unknown")
        self.assertEqual(instructions[3].arguments, ['apk update'])
        self.assertEqual(instructions[4].arguments, ['apk install some packages_${GIT_HASH}'])
        self.assertEqual(instructions[5].ports, ['42'])
        self.assertEqual(instructions[6].arguments, ['/usr/bin/some-server'])
