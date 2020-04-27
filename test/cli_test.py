import unittest

import dockermake.cli


class CliTest(unittest.TestCase):
    def test_parse_no_push(self):
        _, args = dockermake.cli.parse(['-n'])
        self.assertTrue(args.no_push)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.purge)
        self.assertFalse(args.summary)
        self.assertEqual('.', args.work_dir)

    def test_parse_no_push_dry(self):
        _, args = dockermake.cli.parse(['-n', '-d'])
        self.assertTrue(args.no_push)
        self.assertTrue(args.dry_run)
        self.assertFalse(args.purge)
        self.assertFalse(args.summary)
        self.assertEqual('.', args.work_dir)

    def test_parse_no_push_dry_purge(self):
        _, args = dockermake.cli.parse(['-ndp'])
        self.assertTrue(args.no_push)
        self.assertTrue(args.dry_run)
        self.assertTrue(args.purge)
        self.assertFalse(args.summary)
        self.assertEqual('.', args.work_dir)

    def test_parse_no_push_dry_purge_summary(self):
        _, args = dockermake.cli.parse(['-n', '-d', '-p', '-s'])
        self.assertTrue(args.no_push)
        self.assertTrue(args.dry_run)
        self.assertTrue(args.purge)
        self.assertTrue(args.summary)
        self.assertEqual('.', args.work_dir)

    def test_parse_no_push_dry_purge_summary_workdir(self):
        _, args = dockermake.cli.parse(['-n', '-d', '-p', '-s', '-w', 'test'])
        self.assertTrue(args.no_push)
        self.assertTrue(args.dry_run)
        self.assertTrue(args.purge)
        self.assertTrue(args.summary)
        self.assertEqual('test', args.work_dir)

    def test_parse_additional_docker_build_args(self):
        _, args = dockermake.cli.parse(['--build-arg', 'A=42', '--build-arg', 'B=43'])
        self.assertTrue(isinstance(args.docker_build_args, list))
        self.assertEqual(len(args.docker_build_args), 2)
        self.assertEqual(args.docker_build_args[0], 'A=42')
        self.assertEqual(args.docker_build_args[1], 'B=43')
