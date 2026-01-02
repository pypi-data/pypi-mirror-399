import unittest

from nsv.util import escape_seqseq, unescape_seqseq
from nsv.reader import Reader
from nsv.writer import Writer


class TestEscapeOperations(unittest.TestCase):
    """Tests for NSV escape/unescape operations."""

    def test_escape_unescape_invertibility(self):
        """Test unescape ∘ escape = id."""
        test_cases = [
            "",
            "hello",
            "hello\nworld",
            "backslash\\here",
            "both\nand\\here",
            "multiple\n\n\nlines",
            "multiple\\\\\\backslashes",
        ]

        for s in test_cases:
            with self.subTest(string=s):
                escaped = Writer.escape(s)
                recovered = Reader.unescape(escaped)
                self.assertEqual(s, recovered)

    def test_escape_seqseq(self):
        """Test map(map(escape)) operation."""
        seqseq = [["a", "b\n"], ["c\\d", ""]]
        expected = [["a", "b\\n"], ["c\\\\d", "\\"]]
        result = escape_seqseq(seqseq)
        self.assertEqual(expected, result)

        # Verify invertibility
        recovered = unescape_seqseq(result)
        self.assertEqual(seqseq, recovered)


if __name__ == '__main__':
    unittest.main()
