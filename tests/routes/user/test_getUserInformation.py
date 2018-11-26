import requests

from unittest import TestCase
from . import test_token
from .. import BASE_URL


class TestGetUserInformation(TestCase):
    def test_post_working(self):
        """
        this test will pass the user/information method
        """
        url = BASE_URL + "/users/information"

        payload = {
            "token": test_token
        }

        output = requests.post(url, json=payload)

        expected_output = 'hotmapstest@gmail.com'

        assert output.json()['email'] == expected_output

    def test_post_missing_parameters(self):
        """
        this test will fail because of missing parameters
        """
        url = BASE_URL + "/users/information"

        payload = {
            "tokentoto": test_token
        }

        output = requests.post(url, json=payload)

        expected_status= '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_user_unidentified(self):
        """
        this test will fail because of wrong user token
        """
        url = BASE_URL + "/users/information"

        payload = {
            "token": "mybeautifultoken"
        }

        output = requests.post(url, json=payload)

        expected_status= '539'

        assert output.json()['error']['status'] == expected_status

