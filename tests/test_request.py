from unittest import TestCase
from typing import Dict
from copy import copy
from blindpie.request import IRequest, Request


class RequestTest(TestCase):

    def setUp(self):

        self.__params: Dict[str, str] = {
            "param 1": "value 1",
            "param 2": "value 2",
            "param 3": "value 3"
        }
        self.__method: str = "example-method"
        self.__headers: Dict[str, str] = {
            "header 1": "value 1",
            "header 2": "value 2",
            "header 3": "value 3",
        }
        self.__request: IRequest = Request(params=self.__params, method=self.__method, headers=self.__headers)

    def test___str__(self):

        self.assertEqual(
            "params: {:s}, method: {:s}, headers: {:s}".format(str(self.__params), self.__method, str(self.__headers)),
            str(self.__request)
        )

    def test_get_params(self):

        self.assertEqual(
            self.__params,
            self.__request.get_params()
        )

    def test_get_method(self):

        self.assertEqual(
            self.__method,
            self.__request.get_method()
        )

    def test_get_headers(self):

        self.assertEqual(
            self.__headers,
            self.__request.get_headers()
        )

    def test_set_params(self):

        new_params = copy(self.__params)
        new_params["param 2"] = "new value 2"

        self.assertEqual(
            new_params,
            self.__request.set_params(params=new_params).get_params()
        )

    def test_set_method(self):

        new_method = "new-example-method"

        self.assertEqual(
            new_method,
            self.__request.set_method(method=new_method).get_method()
        )

    def test_set_headers(self):

        new_headers = copy(self.__headers)
        new_headers["header 2"] = "new value 2"

        self.assertEqual(
            new_headers,
            self.__request.set_headers(headers=new_headers).get_headers()
        )
