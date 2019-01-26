from unittest import TestCase, mock
from io import StringIO
from threading import Thread
from time import sleep
from contextlib import redirect_stdout
from typing import Dict
from blindpie.logger import ILogger, Logger
from blindpie.frame import IFrame


@mock.patch("blindpie.logger.AnsiEscapeCodes")
class LoggerTest(TestCase):

    def setUp(self):

        self.__mock_ansiescapecodes_attr: Dict[str, str] = {
            "CURSOR_UP.value": "[{:d}UP]",
            "CURSOR_DOWN.value": "[{:d}DOWN]",
            "CURSOR_LEFT.value": "[{:d}LEFT]",
            "CURSOR_RIGHT.value": "[{:d}RIGHT]",
            "CLEAR_LINE.value": "[CLEAR LINE]",
            "CLEAR_SCREEN.value": "[CLEAR SCREEN]"
        }

    def test_log(self, mock_ansiescapecodes):
        """Test whether the frame content is logged completely.
        """

        mock_iframe_content = ["Example of multi-line frame", "---------------------------"]
        mock_iframe: IFrame = mock.Mock()
        mock_iframe.get_height.return_value = len(mock_iframe_content)
        mock_iframe.get_content.return_value = '\n'.join(mock_iframe_content)
        mock_iframe.get_position.return_value = 0

        mock_ansiescapecodes.configure_mock(**self.__mock_ansiescapecodes_attr)

        captured_stdout = StringIO()
        with redirect_stdout(captured_stdout):
            logger: [ILogger, Thread] = Logger()
            logger.log(frame=mock_iframe)
            logger.end()

        frame_content = [
            ''.join([
                self.__mock_ansiescapecodes_attr["CURSOR_LEFT.value"].format(300),
                self.__mock_ansiescapecodes_attr["CLEAR_LINE.value"],
                line,
                self.__mock_ansiescapecodes_attr["CURSOR_DOWN.value"].format(1)
            ]) for line in mock_iframe_content
        ]

        self.assertTrue(''.join(frame_content) in captured_stdout.getvalue())

    def test_log_not_end(self, mock_ansiescapecodes):
        """Test whether the cursor position is restored when logging.
        """

        mock_iframe_content = ["Example of multi-line frame", "---------------------------"]
        mock_iframe: IFrame = mock.Mock()
        mock_iframe.get_height.return_value = len(mock_iframe_content)
        mock_iframe.get_content.return_value = '\n'.join(mock_iframe_content)
        mock_iframe.get_position.return_value = 0

        mock_ansiescapecodes.configure_mock(**self.__mock_ansiescapecodes_attr)

        captured_stdout = StringIO()
        with redirect_stdout(captured_stdout):
            logger: [ILogger, Thread] = Logger()
            logger.log(frame=mock_iframe)
            # Sleep to leave time for the frame to be logged:
            sleep(0.1)
        with redirect_stdout(None):
            logger.end()

        frame_content = [
            ''.join([
                self.__mock_ansiescapecodes_attr["CURSOR_LEFT.value"].format(300),
                self.__mock_ansiescapecodes_attr["CLEAR_LINE.value"],
                line,
                self.__mock_ansiescapecodes_attr["CURSOR_DOWN.value"].format(1)
            ]) for line in mock_iframe_content
        ]
        frame_content.extend([
            self.__mock_ansiescapecodes_attr["CURSOR_LEFT.value"].format(300),
            self.__mock_ansiescapecodes_attr["CURSOR_UP.value"].format(len(mock_iframe_content))
        ])

        self.assertTrue(''.join(frame_content) in captured_stdout.getvalue())

        frame_content[-1] = self.__mock_ansiescapecodes_attr["CURSOR_UP.value"].format(0)

        self.assertTrue(''.join(frame_content) not in captured_stdout.getvalue())

    def test_log_multiple_frames(self, mock_ansiescapecodes):
        """Test whether multiple frames are logged according to their index
        positions.
        """

        mock_iframe_content_1 = ["Example of multi-line frame 1", "---------------------------"]
        mock_iframe_1: IFrame = mock.Mock()
        mock_iframe_1.get_height.return_value = len(mock_iframe_content_1)
        mock_iframe_1.get_content.return_value = '\n'.join(mock_iframe_content_1)
        mock_iframe_1.get_position.return_value = 0

        mock_iframe_content_2 = ["Example of multi-line frame 2", "---------------------------"]
        mock_iframe_2: IFrame = mock.Mock()
        mock_iframe_2.get_height.return_value = len(mock_iframe_content_2)
        mock_iframe_2.get_content.return_value = '\n'.join(mock_iframe_content_2)
        mock_iframe_2.get_position.return_value = 1

        mock_iframe_content_3 = ["Example of single-line frame 1"]
        mock_iframe_3: IFrame = mock.Mock()
        mock_iframe_3.get_height.return_value = len(mock_iframe_content_3)
        mock_iframe_3.get_content.return_value = '\n'.join(mock_iframe_content_3)
        mock_iframe_3.get_position.return_value = 2

        mock_ansiescapecodes.configure_mock(**self.__mock_ansiescapecodes_attr)

        captured_stdout = StringIO()
        with redirect_stdout(captured_stdout):
            logger: [ILogger, Thread] = Logger()
            logger.log(frame=mock_iframe_1)
            logger.log(frame=mock_iframe_3)
            logger.log(frame=mock_iframe_2)
            logger.end()

        frames_contents = [
            ''.join([
                self.__mock_ansiescapecodes_attr["CURSOR_LEFT.value"].format(300),
                self.__mock_ansiescapecodes_attr["CLEAR_LINE.value"],
                line,
                self.__mock_ansiescapecodes_attr["CURSOR_DOWN.value"].format(1)
            ]) for line in mock_iframe_content_1
        ]
        frames_contents.extend([
            ''.join([
                self.__mock_ansiescapecodes_attr["CURSOR_LEFT.value"].format(300),
                self.__mock_ansiescapecodes_attr["CLEAR_LINE.value"],
                line,
                self.__mock_ansiescapecodes_attr["CURSOR_DOWN.value"].format(1)
            ]) for line in mock_iframe_content_2
        ])
        frames_contents.extend([
            ''.join([
                self.__mock_ansiescapecodes_attr["CURSOR_LEFT.value"].format(300),
                self.__mock_ansiescapecodes_attr["CLEAR_LINE.value"],
                line,
                self.__mock_ansiescapecodes_attr["CURSOR_DOWN.value"].format(1)
            ]) for line in mock_iframe_content_3
        ])
        frames_contents.extend([
            self.__mock_ansiescapecodes_attr["CURSOR_LEFT.value"].format(300),
            self.__mock_ansiescapecodes_attr["CURSOR_UP.value"].format(len(mock_iframe_content_1) + len(mock_iframe_content_2) + len(mock_iframe_content_3))
        ])

        self.assertTrue(''.join(frames_contents) in captured_stdout.getvalue())

    def test_log_end(self, mock_ansiescapecodes):
        """Test whether the cursor position is not restored when logging is
        ended.
        """

        mock_iframe_content = ["Example of multi-line frame", "---------------------------"]
        mock_iframe: IFrame = mock.Mock()
        mock_iframe.get_height.return_value = len(mock_iframe_content)
        mock_iframe.get_content.return_value = '\n'.join(mock_iframe_content)
        mock_iframe.get_position.return_value = 0

        mock_ansiescapecodes.configure_mock(**self.__mock_ansiescapecodes_attr)

        captured_stdout = StringIO()
        with redirect_stdout(captured_stdout):
            logger: [ILogger, Thread] = Logger()
            logger.log(frame=mock_iframe)
            logger.end()

        frame_content = [
            ''.join([
                self.__mock_ansiescapecodes_attr["CURSOR_LEFT.value"].format(300),
                self.__mock_ansiescapecodes_attr["CLEAR_LINE.value"],
                line,
                self.__mock_ansiescapecodes_attr["CURSOR_DOWN.value"].format(1)
            ]) for line in mock_iframe_content
        ]
        frame_content.extend([
            self.__mock_ansiescapecodes_attr["CURSOR_LEFT.value"].format(300),
            self.__mock_ansiescapecodes_attr["CURSOR_UP.value"].format(0)
        ])

        self.assertTrue(''.join(frame_content) in captured_stdout.getvalue())

    def test_reset(self, mock_ansiescapecodes):
        """Test whether after a reset is not logged any frame.
        """

        mock_iframe_content = ["Example of multi-line frame", "---------------------------"]
        mock_iframe: IFrame = mock.Mock()
        mock_iframe.get_height.return_value = len(mock_iframe_content)
        mock_iframe.get_content.return_value = '\n'.join(mock_iframe_content)
        mock_iframe.get_position.return_value = 0

        mock_ansiescapecodes.configure_mock(**self.__mock_ansiescapecodes_attr)

        captured_stdout = StringIO()
        with redirect_stdout(captured_stdout):
            logger: [ILogger, Thread] = Logger()
            logger.log(frame=mock_iframe)
            # Sleep to leave time for the frame to be logged:
            sleep(0.1)
            logger.reset()
            sleep(0.1)
            logger.end()

        self.assertTrue(self.__mock_ansiescapecodes_attr["CLEAR_SCREEN.value"] in captured_stdout.getvalue())

        after_clear_index = captured_stdout.getvalue().index(self.__mock_ansiescapecodes_attr["CLEAR_SCREEN.value"])

        frame_content = [
            ''.join([
                self.__mock_ansiescapecodes_attr["CURSOR_LEFT.value"].format(300),
                self.__mock_ansiescapecodes_attr["CLEAR_LINE.value"],
                line,
                self.__mock_ansiescapecodes_attr["CURSOR_DOWN.value"].format(1)
            ]) for line in mock_iframe_content
        ]
        frame_content.extend([
            self.__mock_ansiescapecodes_attr["CURSOR_LEFT.value"].format(300),
            self.__mock_ansiescapecodes_attr["CURSOR_UP.value"].format(0)
        ])

        self.assertTrue(''.join(frame_content) not in captured_stdout.getvalue()[after_clear_index:])

    def test_end(self, mock_ansiescapecodes):
        """Test whether logs after the end of logging are ignored.
        """

        mock_iframe_content = ["Example of multi-line frame", "---------------------------"]
        mock_iframe: IFrame = mock.Mock()
        mock_iframe.get_height.return_value = len(mock_iframe_content)
        mock_iframe.get_content.return_value = '\n'.join(mock_iframe_content)
        mock_iframe.get_position.return_value = 0

        mock_iframe_content_2 = ["Example of single-line frame"]
        mock_iframe_2: IFrame = mock.Mock()
        mock_iframe_2.get_height.return_value = len(mock_iframe_content_2)
        mock_iframe_2.get_content.return_value = '\n'.join(mock_iframe_content_2)
        mock_iframe_2.get_position.return_value = 1

        mock_ansiescapecodes.configure_mock(**self.__mock_ansiescapecodes_attr)

        captured_stdout = StringIO()
        with redirect_stdout(captured_stdout):
            logger: [ILogger, Thread] = Logger()
            logger.log(frame=mock_iframe)
            logger.end()
            logger.log(frame=mock_iframe_2)

        frame_content_2 = [
            ''.join([
                self.__mock_ansiescapecodes_attr["CURSOR_LEFT.value"].format(300),
                self.__mock_ansiescapecodes_attr["CLEAR_LINE.value"],
                line,
                self.__mock_ansiescapecodes_attr["CURSOR_DOWN.value"].format(1)
            ]) for line in mock_iframe_content_2
        ]

        self.assertTrue(''.join(frame_content_2) not in captured_stdout.getvalue())
