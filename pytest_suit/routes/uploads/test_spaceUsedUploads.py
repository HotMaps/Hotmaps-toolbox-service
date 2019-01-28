import requests

from unittest import TestCase
from . import BASE_URL, test_token, test_csv_size

url = BASE_URL + "/users/space_used"


class TestSpaceUsedUploads(TestCase):
    "The class has to be here in order to be run before the deletion of the upload"
    def test_post(self):
        """
        this test will pass the uploads/space_used method
        """
        payload = {
            "token": test_token,
        }

        output = requests.post(url, json=payload)

        expected_output = test_csv_size

        assert output.json()['used_size'] == expected_output

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