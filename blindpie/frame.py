import logging
from abc import ABC, abstractmethod
from typing import List


LOGGER = logging.getLogger(__name__)


class IFrame(ABC):
    """An interface representing a frame in a logger.
    """

    @abstractmethod
    def get_content(self) -> str:
        """Returns the formatted content of this frame.

        :return: str -- the formatted content of this frame
        """

        pass

    @abstractmethod
    def get_height(self) -> int:
        """Returns the height (number of lines) of this frame.

        :return: int -- the height of this frame
        """

        pass

    @abstractmethod
    def get_position(self) -> int:
        """Returns the position of this frame in the frame stack.

        :return: int -- the position of this frame in the frame stack
        """

        pass

    @abstractmethod
    def set_position(self, index: int) -> None:
        """Sets the position of this frame in the frame stack.

        :param index: int -- the position of this frame in the frame stack
        """

        pass


class SimpleFrame(IFrame):
    """A frame whose content is a string.
    """

    def __init__(self, index: int, content: str):
        """Instantiates the frame from the string representation of its content.

        :param index: int -- the position of this frame in the frame stack
        :param content: str -- the string representation of its content
        """

        self.__position: int = index
        self.__content: str = content

    def get_content(self) -> str:

        return self.__content

    def set_content(self, content: str) -> None:

        self.__content = content

    def get_height(self) -> int:

        return len(self.__content.split(sep='\n'))

    def get_position(self) -> int:

        return self.__position

    def set_position(self, index: int) -> None:

        self.__position = index


class IProgressBar(ABC):
    """An interface representing a progress bar.
    """

    @abstractmethod
    def get_progress_bar(self) -> str:
        """Returns the string representation of this progress bar.

        :return: str -- the string representation of this progress bar
        """

        pass

    @abstractmethod
    def set_progress(self, progress: int, total: int, start_message: str = None, end_message: str = None) -> None:
        """Sets the current progress over a total, and any optional messages.

        :param progress: int -- the current progress
        :param total: int -- the maximum obtainable progress
        :param start_message: str -- an optional message to show before the
            progress bar
        :param end_message: str -- an optional message to show after the
            progress bar
        """

        pass


class ProgressBar(IProgressBar):
    """A concrete implementation of a progress bar.
    """

    def __init__(self):
        """Instantiates the progress bar with empty messages and empty progress.
        """

        self._start_message: str = ''
        self._end_message: str = ''
        self._progress: int = 0
        self._total: int = None

    def get_progress_bar(self) -> str:

        progress = 0 if self._total is None else self._progress / self._total * 100
        progress_bar_length = 40
        filled_length = int(progress * progress_bar_length / 100)
        empty_length = progress_bar_length - filled_length
        progress_bar = '█' * filled_length + ' ' * empty_length
        start_message = self._start_message + ' ' if self._start_message != '' else self._start_message
        end_message = ' ' + self._end_message if self._end_message != '' else ''
        return "{:s}{:s} {:.2f}%{:s}".format(start_message, progress_bar, progress, end_message)

    def set_progress(self, progress: int, total: int, start_message: str = None, end_message: str = None) -> None:

        self._progress, self._total = progress, total
        self._start_message = start_message if start_message is not None else self._start_message
        self._end_message = end_message if end_message is not None else self._end_message


class IndeterminateProgressBar(ProgressBar):
    """An indeterminate progress bar.
    """

    def __init__(self):
        """Instantiates the progress bar with empty messages and empty progress.
        """

        super().__init__()
        self.__step = 0
        self.__overflow = 0

    def get_progress_bar(self) -> str:

        LOGGER.debug("Initial step: {:d}".format(self.__step))
        LOGGER.debug("Initial overflow: {:d}".format(self.__overflow))
        progress = 0 if self._total is None else self._progress / self._total * 100
        LOGGER.debug("Progress: {:f}".format(progress))
        progress_bar_length = 40
        filled_length = int(progress * progress_bar_length / 100) if self.__overflow == 0 else self.__overflow
        LOGGER.debug("Filled length: {:d}".format(filled_length))
        empty_length_left = 0 if filled_length == self.__overflow else self.__step
        empty_length_right = progress_bar_length - empty_length_left - filled_length
        LOGGER.debug("Empty length: {:d}; Empty right: {:d}".format(empty_length_left, empty_length_right))
        progress_bar = ' ' * empty_length_left + '█' * filled_length + ' ' * empty_length_right
        self.__step = 0 if filled_length == self.__overflow else self.__step % progress_bar_length + 8
        LOGGER.debug("New step: {:d}".format(self.__step))
        self.__overflow = len(progress_bar) - progress_bar_length
        LOGGER.debug("New overflow: {:d}".format(self.__overflow))
        progress_bar = progress_bar[:progress_bar_length] if self._progress != self._total else '█' * progress_bar_length
        start_message = self._start_message + ' ' if self._start_message != '' else ''
        end_message = ' ' + self._end_message if self._end_message != '' else ''
        LOGGER.debug("Progress bar: {:s}".format("{:s}{:s}{:s}".format(start_message, progress_bar, end_message)))
        return "{:s}{:s}{:s}".format(start_message, progress_bar, end_message)


class ISpinner(ABC):
    """An interface representing a spinner.
    """

    @abstractmethod
    def get_spinner(self) -> str:
        """Returns the string representation of this spinner.

        :return: str -- the string representation of this spinner
        """

        pass

    @abstractmethod
    def set_spinner(self, start_message: str = None, end_message: str = None, end: bool = False) -> None:
        """Sets any optional message.

        :param start_message: str -- an optional message to show before the
            spinner
        :param end_message: str -- an optional message to show after the spinner
        :param end: bool -- if True set this spinner to the final state
        """

        pass


class Spinner(ISpinner):
    """A concrete implementation of a spinner.
    """

    def __init__(self):
        """Instantiates the spinner with empty messages and initial state.
        """

        self._start_message = ''
        self._end_message = ''
        self._step = 0
        self._end = False

    def get_spinner(self):

        states = ['-', '\\', '|', '/']
        start_message = self._start_message + ' ' if self._start_message != '' else ''
        end_message = ' ' + self._end_message if not self._end and self._end_message != '' else self._end_message
        spinner = states[self._step] if not self._end else ''
        self._step = (self._step + 1) % len(states)
        return "{:s}{:s}{:s}".format(start_message, spinner, end_message)

    def set_spinner(self, start_message: str = None, end_message: str = None, end=False) -> None:

        self._start_message = start_message if start_message is not None else self._start_message
        self._end_message = end_message if end_message is not None else self._end_message
        self._end = end


class ProgressFrame(IFrame):
    """A frame which contains multiple progress bars (one for each line).
    """

    def __init__(self, index: int, n_progress_bars: int):
        """Instantiates the frame from the number of progress bars.

        :param index: int -- the position of this frame in the frame stack
        :param n_progress_bars: int -- the number of progress bars
        """

        self._position: int = index
        self._progress_bars: List[IProgressBar] = [ProgressBar() for _ in range(n_progress_bars)]

    def get_content(self) -> str:

        return '\n'.join([p.get_progress_bar() for p in self._progress_bars])

    def get_height(self) -> int:

        return len(self._progress_bars)

    def get_position(self) -> int:

        return self._position

    def set_position(self, index: int):

        self._position = index

    def set_progress(self, progress_bar_index: int, progress: int, total: int, start_message: str = None, end_message: str = None) -> None:
        """Sets the current progress and total of a progress bar, and any
        optional message.

        :param progress_bar_index: int -- the index of the progress bar to
            update
        :param progress: int -- the current progress
        :param total: int -- the maximum obtainable progress
        :param start_message: str -- an optional message to show before the
            progress bar
        :param end_message: str -- an optional message to show after the
            progress bar
        """

        self._progress_bars[progress_bar_index].set_progress(progress=progress, total=total, start_message=start_message, end_message=end_message)


class IndeterminateProgressFrame(ProgressFrame):
    """A frame which contains multiple indeterminate progress bars (one for each
    line).
    """

    def __init__(self, index: int, n_progress_bars: int):
        """Instantiates the frame from the number of progress bars.

        :param index: int -- the position of this frame in the frame stack
        :param n_progress_bars: int -- the number of progress bars
        """

        super().__init__(index=index, n_progress_bars=n_progress_bars)

        self._progress_bars: List[IProgressBar] = [IndeterminateProgressBar() for _ in range(n_progress_bars)]


class SpinnerFrame(IFrame):
    """A frame which contains multiple spinners (one for each line).
    """

    def __init__(self, index: int, n_spinners: int):
        """Instantiates the frame from the number of spinners.

        :param index: int -- the position of this frame in the frame stack
        :param n_spinners: int -- the number of spinners
        """

        self._position: int = index
        self._spinners: List[ISpinner] = [Spinner() for _ in range(n_spinners)]

    def get_content(self) -> str:

        return '\n'.join([p.get_spinner() for p in self._spinners])

    def get_height(self) -> int:

        return len(self._spinners)

    def get_position(self) -> int:

        return self._position

    def set_position(self, index: int) -> None:

        self._position = index

    def set_spinner(self, spinner_index: int, start_message: str = None, end_message: str = None, end: bool = False) -> None:
        """Sets any optional message of a spinner.

        :param spinner_index: int -- the index of the spinner to update
        :param start_message: str -- an optional message to show before the
            spinner
        :param end_message: str -- an optional message to show after the spinner
        :param end: bool -- if True sets the spinner to its final state
        """

        self._spinners[spinner_index].set_spinner(start_message=start_message, end_message=end_message, end=end)


class TableFrame(IFrame):
    """A frame whose content is a table.
    """

    def __init__(self, index: int, table: List[List[str]]):
        """Instantiates the frame given the table to display.

        :param index: int -- the position of this frame in the frame stack
        :param table: List[List[str]] -- the table as a list of rows
        """

        self.__position: int = index
        self.__table: List[List[str]] = table

    def get_content(self) -> str:

        return '\n'.join(['\t'.join(v) for v in self.__table])

    def get_height(self) -> int:

        return len(self.__table)

    def get_position(self) -> int:

        return self.__position

    def set_position(self, index: int):

        self.__position = index

    def set_row(self, row_index: int, column_index: int, value: str):
        """Sets the value of a cell in the table.

        :param row_index: int -- the cell row
        :param column_index: int -- the cell column
        :param value: str -- the new cell value
        """

        self.__table[row_index][column_index] = value
