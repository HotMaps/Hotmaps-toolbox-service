import requests

from unittest import TestCase
from . import BASE_URL, test_token
from .test_addUploads import test_upload_name

url = BASE_URL + "/upload/list"


class TestListUploads(TestCase):
    def test_post(self):
        """
        this test will pass the uploads/list method
        """
        payload = {
            "token": test_token,
        }

        output = requests.post(url, json=payload)

        expected_output = test_upload_name
        assert output.json()['uploads'][0]['name'] == expected_output

    def test_post_missing_parameter(self):
        """
        this test will fail because of missing parameters
        """
        payload = {
            "tokfdsen": test_token,
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_user_unidentified(self):
        """
        this test will fail because the used token is wrong
        """
        payload = {
            "token": 'hey there',
        }

        output = requests.post(url, json=payload)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status
