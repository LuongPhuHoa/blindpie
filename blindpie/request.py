from abc import ABC, abstractmethod
from typing import Dict
from blindpie.defaults import DEFAULT_HEADERS


class IRequest(ABC):
    """An interface representing a request.
    """

    def __str__(self):

        return "params: {:s}, method: {:s}, headers: {:s}".format(str(self.get_params()), self.get_method(), str(self.get_headers()))

    @abstractmethod
    def get_params(self) -> Dict[str, str]:
        """Returns the parameters of this request.

        :return: Dict[str, str] -- the parameters of this request
        """

        pass

    @abstractmethod
    def get_method(self) -> str:
        """Returns the method for this request.

        :return: str -- the method for this request
        """

        pass

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Returns the headers of this request.

        :return: Dict[str, str] -- the headers of this request
        """

        pass

    @abstractmethod
    def set_params(self, params: Dict[str, str]) -> 'IRequest':
        """Sets the parameters of this request.

        :param params: Dict[str, str] -- the new parameters of this request
        :return: IRequest -- this request instance
        """

        pass

    @abstractmethod
    def set_method(self, method: str) -> 'IRequest':
        """Sets the method of this request.

        :param method: str -- the new method of this request
        :return: IRequest -- this request instance
        """

        pass

    @abstractmethod
    def set_headers(self, headers: Dict[str, str]) -> 'IRequest':
        """Sets the headers of this request.

        :param headers: Dict[str, str] -- the new headers of this request
        :return: IRequest -- this request instance
        """

        pass


class Request(IRequest):
    """A concrete representation of a request.
    """

    def __init__(self, params: Dict[str, str], method: str, headers: Dict[str, str] = DEFAULT_HEADERS):
        """Instantiates the request from its parameters.

        :param params: Dict[str, str] -- the parameters of this request
        :param method: str -- the method for this request
        :param headers: Dict[str, str] -- the optional headers of this request
        """

        self.__params: Dict[str, str] = params
        self.__method: str = method
        self.__headers: Dict[str, str] = headers

    def get_params(self) -> Dict[str, str]:

        return self.__params

    def get_method(self) -> str:

        return self.__method

    def get_headers(self) -> Dict[str, str]:

        return self.__headers

    def set_params(self, params: Dict[str, str]) -> IRequest:

        self.__params = params
        return self

    def set_method(self, method: str) -> IRequest:

        self.__method = method
        return self

    def set_headers(self, headers: Dict[str, str]) -> IRequest:

        self.__headers = headers
        return self
