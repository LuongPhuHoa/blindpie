from unittest import TestCase
from bin.blindpie import *


class ArgumentParsingTest(TestCase):

    def test_method(self):

        self.assertEqual("get", method("get"))
        self.assertRaises(ArgumentTypeError, method, "invalid-method")

    def test_params(self):

        self.assertEqual(
            {"param 1": "value 1", "param 2": "value 2"},
            params('{"param 1":"value 1","param 2":"value 2"}')
        )

        self.assertRaises(ArgumentTypeError, params, '[1, 2, 3]')

    def test_headers(self):

        self.assertEqual(
            {"header 1": "value 1", "header 2": "value 2"},
            headers('{"header 1":"value 1","header 2":"value 2"}')
        )

        self.assertRaises(ArgumentTypeError, headers, '[1, 2, 3]')

    def test_threshold(self):

        self.assertEqual(
            2,
            threshold("2")
        )

        self.assertRaises(ArgumentTypeError, threshold, "1")

    def test_max_interval(self):

        self.assertEqual(
            100,
            max_interval("100")
        )

        self.assertRaises(ArgumentTypeError, max_interval, "-1")

    def test_columns(self):

        self.assertEqual(
            ["column 1", "column 2", "column 3"],
            columns("column 1,column 2,column 3")
        )

    def test_from_row(self):

        self.assertEqual(
            0,
            from_row("0")
        )

        self.assertRaises(ArgumentTypeError, from_row, "-1")

    def test_n_rows(self):

        self.assertEqual(
            10,
            n_rows("10")
        )

        self.assertRaises(ArgumentTypeError, n_rows, "0")

    def test_min_row_length(self):

        self.assertEqual(
            0,
            min_row_length("0")
        )

        self.assertRaises(ArgumentTypeError, min_row_length, "-1")

    def test_max_row_length(self):

        self.assertEqual(
            100,
            max_row_length("100")
        )

        self.assertRaises(ArgumentTypeError, max_row_length, "0")
