from unittest import TestCase
from blindpie.frame import *


class SimpleFrameTest(TestCase):

    def setUp(self):

        self.__index = 0
        self.__content = ["Example of multi-line", "SimpleFrame content"]
        self.__frame = SimpleFrame(index=self.__index, content='\n'.join(self.__content))

    def test_get_content(self):

        self.assertEqual('\n'.join(self.__content), self.__frame.get_content())

    def test_set_content(self):

        new_content = '\n'.join(["Example of new multi-line", "SimpleFrame content"])
        self.__frame.set_content(content=new_content)
        self.assertEqual(new_content, self.__frame.get_content())

    def test_get_height(self):

        self.assertEqual(len(self.__content), self.__frame.get_height())

    def test_get_position(self):

        self.assertEqual(self.__index, self.__frame.get_position())

    def test_set_position(self):

        self.__frame.set_position(1)
        self.assertEqual(1, self.__frame.get_position())


class ProgressBarTest(TestCase):

    def setUp(self):

        self.__progress_bar: IProgressBar = ProgressBar()

    def test_get_progress_bar_no_messages(self):

        self.assertEqual(
            ' ' * 40 + " 0.00%",
            self.__progress_bar.get_progress_bar()
        )

    def test_get_progress_bar_both_messages(self):

        start_message = "Example start message"
        end_message = "[example end message]"

        self.__progress_bar.set_progress(42, 333, start_message=start_message, end_message=end_message)

        self.assertEqual(
            start_message + ' ' + '█' * 5 + ' ' * 35 + " 12.61%" + ' ' + end_message,
            self.__progress_bar.get_progress_bar()
        )

        self.__progress_bar.set_progress(42, 42, start_message=start_message, end_message=end_message)

        self.assertEqual(
            start_message + ' ' + '█' * 40 + " 100.00%" + ' ' + end_message,
            self.__progress_bar.get_progress_bar()
        )

    def test_set_progress_bar(self):

        start_message = "Example start message"
        end_message = "[example end message]"

        self.__progress_bar.set_progress(13, 27, start_message=start_message, end_message=end_message)

        self.assertEqual(
            start_message + ' ' + '█' * 19 + ' ' * 21 + " 48.15%" + ' ' + end_message,
            self.__progress_bar.get_progress_bar()
        )


class IndeterminateProgressBarTest(TestCase):

    def setUp(self):

        self.__progress_bar: IProgressBar = IndeterminateProgressBar()

    def test_get_progress_bar(self):

        start_message = "Example start message"
        end_message = "[example end message]"

        self.__progress_bar.set_progress(3, 10, start_message=start_message, end_message=end_message)

        self.assertEqual(
            start_message + ' ' + '█' * 12 + ' ' * 28 + ' ' + end_message,
            self.__progress_bar.get_progress_bar()
        )

    def test_get_progress_bar_following_calls(self):

        start_message = "Example start message"
        end_message = "[example end message]"

        self.__progress_bar.set_progress(3, 10, start_message=start_message, end_message=end_message)

        # Example start message ████████████                             [example end message]
        self.assertEqual(
            start_message + ' ' + '█' * 12 + ' ' * 28 + ' ' + end_message,
            self.__progress_bar.get_progress_bar()
        )

        # Example start message         ████████████                     [example end message]
        self.assertEqual(
            start_message + ' ' + ' ' * 8 + '█' * 12 + ' ' * 20 + ' ' + end_message,
            self.__progress_bar.get_progress_bar()
        )

        # Example start message                 ████████████             [example end message]
        self.assertEqual(
            start_message + ' ' + ' ' * 16 + '█' * 12 + ' ' * 12 + ' ' + end_message,
            self.__progress_bar.get_progress_bar()
        )

        # Example start message                         ████████████     [example end message]
        self.assertEqual(
            start_message + ' ' + ' ' * 24 + '█' * 12 + ' ' * 4 + ' ' + end_message,
            self.__progress_bar.get_progress_bar()
        )

        # Example start message                                 ████████ [example end message]
        self.assertEqual(
            start_message + ' ' + ' ' * 32 + '█' * 8 + ' ' * 0 + ' ' + end_message,
            self.__progress_bar.get_progress_bar()
        )

        # Example start message ████                                     [example end message]
        self.assertEqual(
            start_message + ' ' + ' ' * 0 + '█' * 4 + ' ' * 36 + ' ' + end_message,
            self.__progress_bar.get_progress_bar()
        )

        # Example start message ████                                     [example end message]
        self.assertEqual(
            start_message + ' ' + ' ' * 0 + '█' * 12 + ' ' * 28 + ' ' + end_message,
            self.__progress_bar.get_progress_bar()
        )

    def test_set_progress(self):

        start_message = "Example start message"
        end_message = "[example end message]"

        self.__progress_bar.set_progress(13, 27, start_message=start_message, end_message=end_message)

        self.assertEqual(
            start_message + ' ' + '█' * 19 + ' ' * 21 + ' ' + end_message,
            self.__progress_bar.get_progress_bar()
        )

    def test_get_progress_complete(self):

        start_message = "Example start message"
        end_message = "[example end message]"

        self.__progress_bar.set_progress(1, 1, start_message=start_message, end_message=end_message)

        self.assertEqual(
            start_message + ' ' + '█' * 40 + ' ' + end_message,
            self.__progress_bar.get_progress_bar()
        )


class SpinnerTest(TestCase):

    def setUp(self):

        self.__spinner: ISpinner = Spinner()

    def test_get_spinner_no_messages(self):

        self.assertEqual(
            '-',
            self.__spinner.get_spinner()
        )

    def test_get_spinner_both_messages(self):

        start_message = "Example start message"
        end_message = "[example end message]"

        self.__spinner.set_spinner(start_message=start_message, end_message=end_message)

        self.assertEqual(
            start_message + ' ' + '-' + ' ' + end_message,
            self.__spinner.get_spinner()
        )

    def test_get_spinner_following_calls(self):

        start_message = "Example start message"
        end_message = "[example end message]"

        self.__spinner.set_spinner(start_message=start_message, end_message=end_message)

        self.assertEqual(
            start_message + ' ' + '-' + ' ' + end_message,
            self.__spinner.get_spinner()
        )

        self.assertEqual(
            start_message + ' ' + '\\' + ' ' + end_message,
            self.__spinner.get_spinner()
        )

        self.assertEqual(
            start_message + ' ' + '|' + ' ' + end_message,
            self.__spinner.get_spinner()
        )

        self.assertEqual(
            start_message + ' ' + '/' + ' ' + end_message,
            self.__spinner.get_spinner()
        )

        self.assertEqual(
            start_message + ' ' + '-' + ' ' + end_message,
            self.__spinner.get_spinner()
        )

    def test_set_spinner_end(self):

        start_message = "Example start message"
        end_message = "[example end message]"

        self.__spinner.set_spinner(start_message=start_message, end_message=end_message, end=True)

        self.assertEqual(
            start_message + ' ' + end_message,
            self.__spinner.get_spinner()
        )


class ProgressFrameTest(TestCase):

    def setUp(self):

        self.__index = 0
        self.__n_progress_bars = 5
        self.__frame = ProgressFrame(self.__index, self.__n_progress_bars)

    def test_get_content_no_messages(self):

        self.assertEqual(
            '\n'.join([' ' * 40 + " 0.00%" for _ in range(self.__n_progress_bars)]),
            self.__frame.get_content()
        )

    def test_get_content_both_messages(self):

        progress_bars = [' ' * 40 + " 0.00%" for _ in range(self.__n_progress_bars)]

        start_message = "Example start message"
        end_message = "[example end message]"
        self.__frame.set_progress(progress_bar_index=1, progress=42, total=333, start_message=start_message, end_message=end_message)

        progress_bars[1] = start_message + ' ' + '█' * 5 + ' ' * 35 + " 12.61%" + ' ' + end_message

        self.assertEqual(
            '\n'.join(progress_bars),
            self.__frame.get_content()
        )

    def test_get_height(self):

        self.assertEqual(self.__n_progress_bars, self.__frame.get_height())

    def test_get_position(self):

        self.assertEqual(self.__index, self.__frame.get_position())

    def test_set_position(self):

        self.__frame.set_position(1)
        self.assertEqual(1, self.__frame.get_position())

    def test_set_progress_one_message(self):

        progress_bars = [' ' * 40 + " 0.00%" for _ in range(self.__n_progress_bars)]

        start_message = "Example start message"
        end_message = "[example end message]"
        self.__frame.set_progress(progress_bar_index=2, progress=42, total=333, start_message=start_message, end_message=end_message)

        start_message = "New example start message"
        self.__frame.set_progress(progress_bar_index=2, progress=42, total=333, start_message=start_message)

        progress_bars[2] = start_message + ' ' + '█' * 5 + ' ' * 35 + " 12.61%" + ' ' + end_message

        self.assertEqual(
            '\n'.join(progress_bars),
            self.__frame.get_content()
        )

        end_message = "[new example end message]"
        self.__frame.set_progress(progress_bar_index=2, progress=42, total=333, end_message=end_message)

        progress_bars[2] = start_message + ' ' + '█' * 5 + ' ' * 35 + " 12.61%" + ' ' + end_message

        self.assertEqual(
            '\n'.join(progress_bars),
            self.__frame.get_content()
        )


class IndeterminateProgressFrameTest(TestCase):

    def setUp(self):

        self.__index = 0
        self.__n_progress_bars = 4
        self.__frame: ProgressFrame = IndeterminateProgressFrame(index=self.__index, n_progress_bars=self.__n_progress_bars)

    def test_get_content_both_messages(self):

        progress_bars = [' ' * 40 for _ in range(self.__n_progress_bars)]

        start_message = "Example start message"
        end_message = "[example end message]"

        self.__frame.set_progress(progress_bar_index=1, progress=42, total=333, start_message=start_message, end_message=end_message)

        progress_bars[1] = start_message + ' ' + '█' * 5 + ' ' * 35 + ' ' + end_message

        self.assertEqual(
            '\n'.join(progress_bars),
            self.__frame.get_content()
        )

    def test_get_height(self):

        self.assertEqual(
            self.__n_progress_bars,
            self.__frame.get_height()
        )

    def test_get_position(self):

        self.assertEqual(
            self.__index,
            self.__frame.get_position()
        )

    def test_set_position(self):

        self.__frame.set_position(1)
        self.assertEqual(1, self.__frame.get_position())

    def test_set_progress_one_message(self):

        progress_bars = [' ' * 40 for _ in range(self.__n_progress_bars)]

        start_message = "Example start message"
        end_message = "[example end message]"
        self.__frame.set_progress(progress_bar_index=2, progress=42, total=333, start_message=start_message, end_message=end_message)

        start_message = "New example start message"
        self.__frame.set_progress(progress_bar_index=2, progress=42, total=333, start_message=start_message)

        progress_bars[2] = start_message + ' ' + '█' * 5 + ' ' * 35 + ' ' + end_message

        self.assertEqual(
            '\n'.join(progress_bars),
            self.__frame.get_content()
        )

        end_message = "[new example end message]"
        self.__frame.set_progress(progress_bar_index=2, progress=42, total=333, end_message=end_message)

        progress_bars[2] = start_message + ' ' + ' ' * 8 + '█' * 5 + ' ' * 27 + ' ' + end_message

        self.assertEqual(
            '\n'.join(progress_bars),
            self.__frame.get_content()
        )

    def test_set_progress_complete(self):

        progress_bars = [' ' * 40 for _ in range(self.__n_progress_bars)]

        start_message = "Example start message"
        end_message = "[example end message]"
        self.__frame.set_progress(progress_bar_index=2, progress=42, total=333, start_message=start_message, end_message=end_message)

        self.__frame.get_content()

        start_message = "New example start message"
        self.__frame.set_progress(progress_bar_index=2, progress=1, total=1, start_message=start_message)

        progress_bars[2] = start_message + ' ' + '█' * 40 + ' ' + end_message

        self.assertEqual(
            '\n'.join(progress_bars),
            self.__frame.get_content()
        )


class TableFrameTest(TestCase):

    def setUp(self):

        self.__index = 0
        self.__content = [
            ["Example key 1", "42", "43"],
            ["Example key 2", "333"]
        ]
        self.__frame = TableFrame(self.__index, self.__content)

    def test_get_content(self):

        self.assertEqual(
            "{:s}\t{:s}\t{:s}\n{:s}\t{:s}".format(self.__content[0][0], self.__content[0][1], self.__content[0][2], self.__content[1][0], self.__content[1][1]),
            self.__frame.get_content()
        )

    def test_get_height(self):

        self.assertEqual(len(self.__content), self.__frame.get_height())

    def test_get_position(self):

        self.assertEqual(self.__index, self.__frame.get_position())

    def test_set_position(self):

        self.__frame.set_position(1)
        self.assertEqual(1, self.__frame.get_position())

    def test_set_row(self):

        new_value = "7"
        self.__frame.set_row(row_index=0, column_index=2, value=new_value)

        self.assertEqual(
            "{:s}\t{:s}\t{:s}\n{:s}\t{:s}".format(self.__content[0][0], self.__content[0][1], new_value, self.__content[1][0], self.__content[1][1]),
            self.__frame.get_content()
        )
