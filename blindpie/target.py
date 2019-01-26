import logging
import requests
from abc import ABC, abstractmethod
from typing import List
from concurrent.futures import ThreadPoolExecutor, wait
from random import triangular
from time import sleep, time
from blindpie.request import IRequest
from blindpie.defaults import DEFAULT_MAX_INTERVAL, DEFAULT_MAX_THREADS


LOGGER = logging.getLogger(__name__)


class ITarget(ABC):
    """An interface representing a target website.
    """

    @abstractmethod
    def get_url(self) -> str:
        """Returns the URL of this target.

        :return: str -- the URL of this target
        """

    @abstractmethod
    def get_response_time(self, request: IRequest) -> float:
        """Returns the response time of the target to a request in ms.

        :param request: IRequest -- the request to make
        :return: int -- the response time to the request in ms
        :raises: TargetUnavailableException -- when the target seems to be
            unavailable
        """

        pass

    @abstractmethod
    def get_response_times(self, requests_: List[IRequest], max_interval: int = DEFAULT_MAX_INTERVAL, max_threads: int = DEFAULT_MAX_THREADS) -> List[float]:
        """Returns the response times of the target to multiple requests in ms.

        :param requests_: List[IRequest] -- the list of requests to make
        :param max_interval: int -- the max time to wait between each request in
            ms
        :param max_threads: int -- the max number of requests to make
            concurrently
        :return: List[int] -- the response times to the requests in ms
        :raises: TargetUnavailableException -- when the target seems to be
            unavailable
        """

        pass


class TargetUnavailableException(Exception):
    """Exception thrown when a target seems to be unavailable.
    """

    def __init__(self, target: ITarget, request: IRequest, status: str):
        """Instantiates the exception from a target, the request, and its
        status.

        :param target: ITarget -- the target which is unavailable
        :param request: IRequest -- the request which raised the exception
        :param status: str -- the target status
        """

        self.target: ITarget = target
        self.request: IRequest = request
        self.status: str = status

    def __str__(self):

        return "Target '{:s}' was unavailable ('{:s}') during request '{:s}'".format(self.target.get_url(), self.status, str(self.request))


class Target(ITarget):
    """A concrete representation of a target website.
    """

    def __init__(self, url: str):
        """Instantiates a target from its URL.

        :param url: str -- the target URL
        """

        self.url = url

    def _get_response_time(self, request: IRequest) -> float:
        """Returns the response time of the target to a request in ms.

        :param request: IRequest -- the request to make
        :return: int -- the response time to the request in ms
        :raises: TargetUnavailableException -- when the target seems to be
            unavailable
        """

        try:
            start_time = time()
            response = requests.request(url=self.get_url(), params=request.get_params(), method=request.get_method(), headers=request.get_headers())
            end_time = time() - start_time
            response.raise_for_status()
            LOGGER.debug("Target response time: {:f} ms".format(end_time * 1000))
            return end_time * 1000
        except requests.HTTPError as e:
            raise TargetUnavailableException(target=self, request=request, status=str(e.response.status_code))

    def get_url(self) -> str:

        return self.url

    def get_response_time(self, request: IRequest) -> float:

        return self._get_response_time(request)

    def get_response_times(self, requests_: List[IRequest], max_interval: int = DEFAULT_MAX_INTERVAL, max_threads: int = DEFAULT_MAX_THREADS) -> List[float]:

        with ThreadPoolExecutor(max_workers=max_threads) as thread_pool:
            threads = list()
            for r in requests_:
                delay = triangular(max_interval / 2, max_interval)
                sleep(delay / 1000)
                LOGGER.debug("Delayed for: {:f} ms".format(delay))
                threads.append(thread_pool.submit(self._get_response_time, request=r))
            wait(threads)

        return [t.result() for t in threads]
