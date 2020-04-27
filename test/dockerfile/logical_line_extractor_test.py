import unittest

from dockermake.dockerfile.logical_line_extractor import LogicalLineExtractor


class LogicalLineExtractorTest(unittest.TestCase):
    def test_logical_line_extraction(self):
        context = r"""# this is a comment
          # comment with leading whitespace
        line 3
        line 4

        line 6 # has a comment
        line 7 \# does not have a comment
        line 8 \
          continues over three \
          physical lines

        line 12 \
          continues over five \
          # comment without backslash
          # comment with backslash \
          physical lines with two comment lines

        line 18 \

          continues over two physical lines, with a blank in between

        line 22 doesn't continue \\
        line \23 in\cludes \escapes (and also a\ bug).
            line 24 also has a comment # which gets rid of this backslash \
        and lastly line 25 \
        holding "a string" \
        and 'another string'
        """
        lines = LogicalLineExtractor.parse_dockerfile(context)
        self.assertEqual(len(lines), 11)
        self.assertEqual(lines[0], ('line 3', 3))
        self.assertEqual(lines[1], ('line 4', 4))
        self.assertEqual(lines[2], ('line 6', 6))
        self.assertEqual(lines[3], ('line 7 \# does not have a comment', 7))
        self.assertEqual(lines[4], ('line 8 continues over three physical lines', 8))
        self.assertEqual(lines[5], ('line 12 continues over five physical lines with two comment lines', 12))
        self.assertEqual(lines[6], ('line 18 continues over two physical lines, with a blank in between', 18))
        self.assertEqual(lines[7], ('line 22 doesn\'t continue \\\\', 22))
        self.assertEqual(lines[8], ('line \\23 in\cludes \escapes (and also a\\bug).', 23))
        self.assertEqual(lines[9], ('line 24 also has a comment', 24))
        self.assertEqual(lines[10], ('and lastly line 25 holding \"a string\" and \'another string\'', 25))

    def test_logical_line_extraction_with_single_quoted_comment(self):
        context = r"""
            RUN sed -i 's##' somescript.sh \
             && echo 

        """
        lines = LogicalLineExtractor.parse_dockerfile(context)
        self.assertEqual(len(lines), 1)

    def test_logical_line_extraction_with_double_quoted_comment(self):
        context = r"""
            RUN sed -i "s##" somescript.sh \
             && echo 

        """
        lines = LogicalLineExtractor.parse_dockerfile(context)
        self.assertEqual(len(lines), 1)

    def test_logical_line_extraction_quoted_linebreak(self):
        context = r"""
            RUN "echo \
             hello"

        """
        lines = LogicalLineExtractor.parse_dockerfile(context)
        self.assertEqual(len(lines), 1)
