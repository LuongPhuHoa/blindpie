from unittest import TestCase, mock
from typing import Dict, List
from copy import deepcopy
from blindpie.target import ITarget
from blindpie.request import IRequest
from blindpie.payloadbuilder import PayloadBuilder
from blindpie.defaults import *


class PayloadBuilderTest(TestCase):

    def setUp(self):

        self.__mock_itarget_attr = {
            "get_url.return_value": "http://example-target.com",
            "get_response_time": None,
            "get_response_times": None
        }

        self.__mock_irequest_attr = {
            "get_params.return_value": {"param 1": "default value 1", "param 2": "default value 2"},
            "get_method.return_value": "example method",
            "get_headers.return_value": {"header 1": "value 1", "header 2": "value 2"},
            "set_params": None,
            "set_method": None,
            "set_headers": None
        }

    @mock.patch("blindpie.target.ITarget")
    def test_set_threshold(self, mock_itarget: [ITarget, mock.Mock]):

        mock_itarget.configure_mock(**self.__mock_itarget_attr)

        threshold = 2
        target = mock_itarget

        payload_builder = PayloadBuilder(target=target)

        payload_builder.set_threshold(threshold=threshold)

        self.assertEqual(
            threshold,
            payload_builder.get_threshold()
        )

    @mock.patch("blindpie.target.ITarget")
    @mock.patch("blindpie.request.IRequest")
    def test_get_sleep_time(self, mock_itarget: [ITarget, mock.Mock], mock_irequest: [IRequest, mock.Mock]):

        mock_itarget.configure_mock(**self.__mock_itarget_attr)
        mock_irequest.configure_mock(**self.__mock_irequest_attr)

        target_response_time = 42

        mock_itarget.get_response_time = mock.Mock()
        mock_itarget.get_response_time.return_value = target_response_time

        threshold = 2
        target = mock_itarget
        default_request = mock_irequest

        payload_builder = PayloadBuilder(target=target, threshold=threshold)

        self.assertEqual(
            target_response_time * threshold,
            payload_builder.get_sleep_time(default_request=default_request)
        )

    @mock.patch("blindpie.target.ITarget")
    @mock.patch("blindpie.request.IRequest")
    def test_get_reference_resp_time(self, mock_itarget: [ITarget, mock.Mock], mock_irequest: [IRequest, mock.Mock]):

        mock_itarget.configure_mock(**self.__mock_itarget_attr)
        mock_irequest.configure_mock(**self.__mock_irequest_attr)

        target_response_time = 42

        mock_itarget.get_response_time = mock.Mock()
        mock_itarget.get_response_time.return_value = target_response_time

        threshold = 2
        target = mock_itarget
        default_request = mock_irequest

        payload_builder = PayloadBuilder(target=target, threshold=threshold)

        self.assertEqual(
            target_response_time,
            payload_builder.get_reference_resp_time(default_request=default_request)
        )

    @mock.patch("blindpie.target.ITarget")
    @mock.patch("blindpie.request.IRequest")
    def test_get_test_payload(self, mock_itarget: [ITarget, mock.Mock], mock_irequest: [IRequest, mock.Mock]):
        """Test whether it is returned the correct test payload for a parameter.
        """

        param = "param 1"
        threshold = 2
        sqli_payload = DEFAULT_TEST_PAYLOADS[0]
        reference_resp_time_ms = 3
        affirmative_resp_time_ms = 42

        def mock_get_response_time(request: IRequest):

            if request.get_params()[param] == sqli_payload.format(sleep_time=reference_resp_time_ms * threshold / 1000):
                return affirmative_resp_time_ms
            else:
                return reference_resp_time_ms

        def mock_get_response_times(requests_: List[IRequest], **_):

            return [mock_get_response_time(r) for r in requests_]

        def mock_set_params(params: Dict[str, str]):

            mock_irequest_copy = deepcopy(mock_irequest)
            mock_irequest_copy.get_params.return_value = params
            return mock_irequest_copy

        mock_itarget.configure_mock(**self.__mock_itarget_attr)
        mock_irequest.configure_mock(**self.__mock_irequest_attr)

        mock_itarget.get_response_time = mock_get_response_time
        mock_itarget.get_response_times = mock_get_response_times
        mock_irequest.set_params = mock_set_params

        target = mock_itarget
        default_request = mock_irequest

        payload_builder = PayloadBuilder(target=target, threshold=threshold)

        self.assertEqual(
            sqli_payload,
            payload_builder.get_test_payload(default_request=default_request, param="param 1")
        )

    @mock.patch("blindpie.target.ITarget")
    @mock.patch("blindpie.request.IRequest")
    def test_get_fetch_char_payload(self, mock_itarget: [ITarget, mock.Mock], mock_irequest: [IRequest, mock.Mock]):
        """Test whether it is returned the correct fetch char payload for a parameter.
        """

        param = "param 1"
        threshold = 2
        sqli_payload = DEFAULT_TEST_PAYLOADS[1]
        fetch_char_payload = DEFAULT_FETCH_CHAR_PAYLOADS[1]
        reference_resp_time_ms = 3
        affirmative_resp_time_ms = 42

        def mock_get_response_time(request: IRequest):

            if request.get_params()[param] == sqli_payload.format(sleep_time=reference_resp_time_ms * threshold / 1000):
                return affirmative_resp_time_ms
            else:
                return reference_resp_time_ms

        def mock_get_response_times(requests_: List[IRequest], **_):

            return [mock_get_response_time(r) for r in requests_]

        def mock_set_params(params: Dict[str, str]):

            mock_irequest_copy = deepcopy(mock_irequest)
            mock_irequest_copy.get_params.return_value = params
            return mock_irequest_copy

        mock_itarget.configure_mock(**self.__mock_itarget_attr)
        mock_irequest.configure_mock(**self.__mock_irequest_attr)

        mock_itarget.get_response_time = mock_get_response_time
        mock_itarget.get_response_times = mock_get_response_times
        mock_irequest.set_params = mock_set_params

        target = mock_itarget
        default_request = mock_irequest

        payload_builder = PayloadBuilder(target=target, threshold=threshold)

        self.assertEqual(
            fetch_char_payload,
            payload_builder.get_fetch_char_payload(default_request=default_request, param="param 1")
        )

    @mock.patch("blindpie.target.ITarget")
    @mock.patch("blindpie.request.IRequest")
    def test_get_fetch_row_payload(self, mock_itarget: [ITarget, mock.Mock], mock_irequest: [IRequest, mock.Mock]):
        """Test whether it is returned the correct fetch row length payload for a parameter.
        """

        param = "param 1"
        threshold = 2
        sqli_payload = DEFAULT_TEST_PAYLOADS[1]
        fetch_row_length_payload = DEFAULT_FETCH_ROW_LENGTH_PAYLOADS[1]
        reference_resp_time_ms = 3
        affirmative_resp_time_ms = 42

        def mock_get_response_time(request: IRequest):

            if request.get_params()[param] == sqli_payload.format(
                    sleep_time=reference_resp_time_ms * threshold / 1000):
                return affirmative_resp_time_ms
            else:
                return reference_resp_time_ms

        def mock_get_response_times(requests_: List[IRequest], **_):

            return [mock_get_response_time(r) for r in requests_]

        def mock_set_params(params: Dict[str, str]):

            mock_irequest_copy = deepcopy(mock_irequest)
            mock_irequest_copy.get_params.return_value = params
            return mock_irequest_copy

        mock_itarget.configure_mock(**self.__mock_itarget_attr)
        mock_irequest.configure_mock(**self.__mock_irequest_attr)

        mock_itarget.get_response_time = mock_get_response_time
        mock_itarget.get_response_times = mock_get_response_times
        mock_irequest.set_params = mock_set_params

        target = mock_itarget
        default_request = mock_irequest

        payload_builder = PayloadBuilder(target=target, threshold=threshold)

        self.assertEqual(
            fetch_row_length_payload,
            payload_builder.get_fetch_row_length_payload(default_request=default_request, param="param 1")
        )

    def test_get_columns_concat_single_column(self):

        columns = ["example_column"]

        self.assertEqual(
            columns[0],
            PayloadBuilder.get_columns_concat(columns=columns)[0]
        )

        self.assertEqual(
            '\t',
            PayloadBuilder.get_columns_concat(columns=columns)[1]
        )

    def test_get_columns_concat_multiple_columns(self):

        columns = ["example_column1", "example_column2", "example_column3"]

        self.assertEqual(
            "concat(example_column1,char(9),example_column2,char(9),example_column3)",
            PayloadBuilder.get_columns_concat(columns=columns)[0]
        )

        self.assertEqual(
            '\t',
            PayloadBuilder.get_columns_concat(columns=columns)[1]
        )
