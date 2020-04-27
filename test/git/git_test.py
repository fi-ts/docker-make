import unittest
import subprocess

from dockermake.git.git import get_gitsha1_hash_of_head


class GitTest(unittest.TestCase):
    def test_get_gitsha1_hash_of_head(self):
        process = subprocess.Popen("git rev-parse --short=8 HEAD", shell=True, stdout=subprocess.PIPE, encoding='UTF-8')
        output, _ = process.communicate()

        sha1Hash = get_gitsha1_hash_of_head()

        self.assertEqual(output.strip(), sha1Hash)
