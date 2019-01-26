from abc import ABC, abstractmethod
from typing import List, Dict


class OutputFormatter(ABC):
    """An interface to format a table.
    """

    @abstractmethod
    def get_formatted_header(self) -> str:
        """Returns the table header as a formatted string.

        :return: str -- the header as a formatted string
        """

        pass

    @abstractmethod
    def get_formatted_row(self, row: Dict[str, str]) -> str:
        """Returns a row as a formatted string.

        :param row: Dict[str, str] -- a dictionary of (column name, row value)
        :return: str -- the row as a formatted string
        """

        pass

    @abstractmethod
    def get_formatted_footer(self) -> str:
        """Returns the table footer as a formatted string.

        :return: str -- the footer as a formatted string
        """

        pass


class TsvOutputFormatter(OutputFormatter):
    """A TSV output formatter.
    """

    def __init__(self, columns: List[str]):
        """Instantiates the output formatter given the columns of the table to
        format.

        :param columns: List[str] -- the names of the columns of the table to
            format
        """

        self.__columns: List[str] = columns

    def get_formatted_header(self) -> str:

        return '\t'.join(self.__columns)

    def get_formatted_row(self, row: Dict[str, str]) -> str:

        return '\t'.join([row[column] for column in self.__columns])

    def get_formatted_footer(self) -> str:

        return ''
