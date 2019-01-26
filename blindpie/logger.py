import sys
from abc import ABC, abstractmethod
from threading import Thread, Event, Lock
from collections import OrderedDict
from queue import Queue, Empty
from copy import copy
from typing import Dict
from shutil import get_terminal_size
from time import sleep
from signal import signal, SIGINT
from enum import Enum
from blindpie.frame import IFrame


class ILogger(ABC):
    """An interface representing a logger.
    """

    @abstractmethod
    def log(self, frame: IFrame) -> None:
        """Logs a frame.

        The position of the frame in the frame stack will be the position given
        by the frame.

        :param frame: IFrame -- the frame to log
        """

        pass

    @abstractmethod
    def reset(self) -> None:
        """Clears the logging screen.

        The frame stack and the update queue are emptied.
        """

        pass

    @abstractmethod
    def end(self) -> None:
        """Stops the logger.

        The update queue is emptied, then the logger is stopped. Following logs
        are ignored.
        """

        pass


class _Cursor:
    """Represents the cursor position in the terminal.
    """

    def __init__(self):

        self.x: int = 0
        """Row index"""
        self.y: int = 0
        """Column index"""


class AnsiEscapeCodes(Enum):
    """ANSI escape codes for cursor movement in the terminal.
    """

    CURSOR_UP = "\u001b[{:d}A"
    CURSOR_DOWN = "\u001b[{:d}B"
    CURSOR_LEFT = "\u001b[{:d}D"
    CURSOR_RIGHT = "\u001b[{:d}C"
    CLEAR_LINE = "\u001b[0K"
    CLEAR_SCREEN = "\u001b[0J"


class Logger(ILogger, Thread):
    """A concrete implementation of a logger.
    """

    def __init__(self):

        # Handle Ctrl+C:
        signal(SIGINT, self._signal_handler)

        Thread.__init__(self)
        self.__frames_stack: Dict[int, IFrame] = dict()
        """Dictionary of (frame position, frame)"""
        self.__frames_stack_lock: Lock = Lock()
        """Lock for frames stack access"""
        self.__update_queue: Queue[IFrame] = Queue(-1)
        """Queue of frames to update"""
        self.__update_queue_lock: Lock = Lock()
        """Lock for update queue access"""
        self.__cursor_position: _Cursor = _Cursor()
        """Current cursor position"""
        self.__stop: Event = Event()
        """Flag to stop logging"""

        self.__stop.clear()
        super(Logger, self).start()

    def _signal_handler(self, _, __):
        """Handler for the Ctrl+C keystroke event.

        Stops the logger.
        """

        self.end()

    def _log(self, end: bool = False):
        """Logs the frames in the frame stack.

        The cursor position is finally restored to the initial value.

        :param end: bool -- if True do not restore the previous cursor position
        """

        prev_cursor_position = copy(self.__cursor_position)
        sys.stdout.write(AnsiEscapeCodes.CURSOR_LEFT.value.format(300))
        self.__cursor_position.y = 0

        with self.__frames_stack_lock:
            for frame in [self.__frames_stack[position] for position in sorted(self.__frames_stack.keys())]:

                max_width = get_terminal_size().columns

                for line in frame.get_content().split('\n'):
                    sys.stdout.write(AnsiEscapeCodes.CLEAR_LINE.value)
                    line = line[:max_width]
                    sys.stdout.write(line)
                    self.__cursor_position.y = len(line) - 1
                    sys.stdout.write(AnsiEscapeCodes.CURSOR_DOWN.value.format(1))
                    self.__cursor_position.x += 1
                    sys.stdout.write(AnsiEscapeCodes.CURSOR_LEFT.value.format(300))
                    self.__cursor_position.y = 0

                sleep(0.05)

        # Restore previous cursor position:
        if not end:
            sys.stdout.write(AnsiEscapeCodes.CURSOR_UP.value.format(self.__cursor_position.x - prev_cursor_position.x))
        else:
            sys.stdout.write(AnsiEscapeCodes.CURSOR_UP.value.format(0) + '\n')
        self.__cursor_position.x = prev_cursor_position.x

        sys.stdout.flush()

    def run(self):

        while not self.__stop.is_set():

            try:
                while not self.__update_queue.empty():
                    frame = self.__update_queue.get(block=False)
                    with self.__frames_stack_lock:
                        self.__frames_stack[frame.get_position()] = frame
                    self.__update_queue.task_done()
                self._log()
            except Empty:
                continue

        self._log(end=True)

    def log(self, frame: IFrame):

        if not self.__stop.is_set():
            self.__update_queue.put(frame, block=False)

    def reset(self):

        with self.__frames_stack_lock:
            self.__frames_stack: Dict[int, IFrame] = OrderedDict()
        with self.__update_queue_lock:
            self.__update_queue = Queue(-1)

        print(AnsiEscapeCodes.CLEAR_SCREEN.value, end='')

    def end(self):

        self.__update_queue.join()
        self.__stop.set()
        self.join()
