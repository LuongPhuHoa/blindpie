from unittest import TestCase
from blindpie.outputformatter import OutputFormatter, TsvOutputFormatter


class TsvOutputFormatterTest(TestCase):

    def setUp(self):

        self.__columns = ["column 1", "column 2", "column 3"]
        self.__rows = [
            {"column 1": "value 11", "column 2": "value 12", "column 3": "value 13"},
            {"column 1": "value 21", "column 2": "value 22", "column 3": "value 23"},
            {"column 1": "value 31", "column 2": "value 32", "column 3": "value 33"}
        ]

        self.__output_formatter: OutputFormatter = TsvOutputFormatter(self.__columns)

    def test_get_formatted_header(self):

        self.assertEqual(
            "{:s}\t{:s}\t{:s}".format(self.__columns[0], self.__columns[1], self.__columns[2]),
            self.__output_formatter.get_formatted_header()
        )

    def test_get_formatted_row(self):

        self.assertEqual(
            "{column 1}\t{column 2}\t{column 3}".format(**self.__rows[2]),
            self.__output_formatter.get_formatted_row(self.__rows[2])
        )

    def test_get_formatted_footer(self):

        self.assertEqual('', self.__output_formatter.get_formatted_footer())
