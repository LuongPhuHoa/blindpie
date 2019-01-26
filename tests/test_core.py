import os
from unittest import TestCase, mock, skip
from blindpie.logger import ILogger
from blindpie.request import IRequest, Request
from blindpie.core import Blindpie


_DVWA_PHPSESSID = "80ht32u7nja8oqv1ldkoslpd86"
_DVWA_URL = "http://192.168.1.105/vulnerabilities/sqli_blind/"
_DVWA_PARAMS = {"id": "1", "Submit": "Submit"}
_DVWA_METHOD = "get"
_DVWA_HEADERS = {"Cookie": "security=medium;PHPSESSID={:s}".format(_DVWA_PHPSESSID)}

_DVWA_TABLE = "users"
_DVWA_COLUMNS = ["first_name", "last_name", "user", "password"]


@skip("At the moment requires a DVWA instance to be tested")
class BlindpieTest(TestCase):

    def setUp(self):

        self.__mock_ilogger: ILogger = mock.Mock()
        self.__mock_ilogger.log.return_value = None
        self.__mock_ilogger.reset.return_value = None
        self.__mock_ilogger.end.return_value = None

        self.__default_request: IRequest = Request(params=_DVWA_PARAMS, method=_DVWA_METHOD, headers=_DVWA_HEADERS)

        self.__url = _DVWA_URL
        self.__params = _DVWA_PARAMS
        self.__blindpie = Blindpie(url=self.__url, params=self.__params, logger=self.__mock_ilogger)

    def test_fetch_char(self):

        self.assertEqual(
            'G',
            self.__blindpie.fetch_char(default_request=self.__default_request, param=list(_DVWA_PARAMS.keys())[0], table=_DVWA_TABLE, columns=_DVWA_COLUMNS, row_index=1, char_index=1)
        )

    def test_fetch_row_length(self):

        self.assertEqual(
            6,
            self.__blindpie.fetch_row_length(default_request=self.__default_request, param=list(_DVWA_PARAMS.keys())[0], table=_DVWA_TABLE, columns=_DVWA_COLUMNS[:1], row_index=1)
        )

    def test_fetch_row(self):

        row_dict = self.__blindpie.fetch_row(default_request=self.__default_request, param=list(_DVWA_PARAMS.keys())[0], table=_DVWA_TABLE, columns=_DVWA_COLUMNS[:1], row_index=1)

        self.assertEqual(
            "Gordon",
            row_dict[_DVWA_COLUMNS[0]]
        )

    def test_test(self):

        self.assertEqual(
            [list(_DVWA_PARAMS.keys())[0]],
            self.__blindpie.test(default_request=self.__default_request)
        )

    def test_fetch_table(self):

        temp_output_path = "./blindpie.temp"

        self.__blindpie.fetch_table(default_request=self.__default_request, param=list(_DVWA_PARAMS.keys())[0], table=_DVWA_TABLE, columns=_DVWA_COLUMNS[:2], n_rows=2, output_path=temp_output_path)

        with open(temp_output_path) as temp_output_file:
            content = temp_output_file.read()

        self.assertEqual(
            '\n'.join(['\t'.join(_DVWA_COLUMNS[:2]), '\t'.join(["admin", "admin"]), '\t'.join(["Gordon", "Brown"])]) + '\n',
            content
        )

        os.remove(temp_output_path)
