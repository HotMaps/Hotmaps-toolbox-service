import requests
from unittest import TestCase
from . import BASE_URL, test_token, test_upload_name

url = BASE_URL + "/upload/download"


class TestDownload(TestCase):
    def test_post_working(self):
        """
        this test will pass the upload/download method
        """
        payload = {
            "token": test_token,
            "upload_name": test_upload_name
        }

        output = requests.post(url, json=payload)
        expected_output = "name, size\r\ntest, 10"
        assert output.content == expected_output

    def test_download_missing_parameter(self):
        """
        this test will fail because the given parameters are wrong
        """
        payload = {
            "usafrl": test_upload_name,
            "togfdken": test_token,
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_download_user_unidentified(self):
        """
        this test will pass the uploads/add method
        """
        payload = {
            "upload_name": test_upload_name,
            "token": "ThisIsAWrongToken",
        }

        output = requests.post(url, json=payload)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status

    def test_download_upload_not_existing(self):
        """
        this test will pass the uploads/add method
        """
        payload = {
            "upload_name": "thisisarandomurl",
            "token": test_token,
        }

        output = requests.post(url, json=payload)

        expected_status = '543'

        assert output.json()['error']['status'] == expected_status

