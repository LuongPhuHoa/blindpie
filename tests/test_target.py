import requests
from unittest import TestCase, mock
from time import sleep, time
from blindpie.target import ITarget, Target, TargetUnavailableException


class TargetTest(TestCase):

    def setUp(self):

        self.__url = "https://example-target.com"
        self.__params = {"param 1": "value 1", "param 2": "value 2"}
        self.__method = "example-method"
        self.__headers = {"header 1": "value 1", "header 2": "value 2"}
        self.__target: ITarget = Target(self.__url)

    def test_get_url(self):

        self.assertEqual(self.__url, self.__target.get_url())

    @mock.patch("blindpie.request.IRequest")
    def test_get_response_time_target_available(self, mock_irequest):

        target_resp_time_ms = 50

        def mock_request(*_, **__):
            sleep(target_resp_time_ms / 1000)
            return mock.Mock()

        mock_irequest.get_params.return_value = self.__params
        mock_irequest.get_method.return_value = self.__method
        mock_irequest.get_headers.return_value = self.__headers

        with mock.patch("requests.request", side_effect=mock_request) as _:
            self.assertGreater(self.__target.get_response_time(request=mock_irequest), target_resp_time_ms)

    @mock.patch("blindpie.request.IRequest")
    def test_get_response_time_target_unavailable(self, mock_irequest):

        target_resp_time_ms = 50

        def mock_raise_for_status(*_, **__):
            mock_response = mock.Mock()
            mock_response.status_code = "example status code"
            raise requests.HTTPError(response=mock_response)

        def mock_request(*_, **__):
            sleep(target_resp_time_ms / 1000)
            mock_response = mock.Mock()
            mock_response.raise_for_status = mock_raise_for_status
            return mock_response

        mock_irequest.get_params.return_value = self.__params
        mock_irequest.get_method.return_value = self.__method
        mock_irequest.get_headers.return_value = self.__headers

        with mock.patch("requests.request", side_effect=mock_request) as _:
            self.assertRaises(TargetUnavailableException, self.__target.get_response_time, request=mock_irequest)

    @mock.patch("blindpie.request.IRequest")
    def test_get_response_times(self, mock_irequest):

        target_resp_times_ms = [50, 45, 40, 35]

        idx = 0

        def mock_request(*_, **__):
            nonlocal idx
            sleep(target_resp_times_ms[idx] / 1000)
            idx += 1
            return mock.Mock()

        mock_irequest.get_params.return_value = self.__params
        mock_irequest.get_method.return_value = self.__method
        mock_irequest.get_headers.return_value = self.__headers

        with mock.patch("requests.request", side_effect=mock_request) as _:
            requests_ = [mock_irequest] * len(target_resp_times_ms)
            resp_times_ms = self.__target.get_response_times(requests_)
            for i in range(len(target_resp_times_ms)):
                self.assertGreater(resp_times_ms[i], target_resp_times_ms[i])

    @mock.patch("blindpie.request.IRequest")
    def test_get_response_times_max_interval(self, mock_irequest):
        """Test whether each request is actually with some interval.
        """

        target_resp_times_ms = [50, 45, 40, 35]
        max_interval = 50

        idx = 0

        def mock_request(*_, **__):
            nonlocal idx
            sleep(target_resp_times_ms[idx] / 1000)
            idx += 1
            return mock.Mock()

        mock_irequest.get_params.return_value = self.__params
        mock_irequest.get_method.return_value = self.__method
        mock_irequest.get_headers.return_value = self.__headers

        with mock.patch("requests.request", side_effect=mock_request) as _:
            requests_ = [mock_irequest] * len(target_resp_times_ms)
            start_time = time()
            self.__target.get_response_times(requests_, max_interval=max_interval)
            end_time = time() - start_time

        self.assertGreater(end_time * 1000, sum(target_resp_times_ms))
