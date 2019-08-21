import requests

from unittest import TestCase
from . import BASE_URL, test_token, test_session_name

url = BASE_URL + '/scenarios/list'


class TestListSession(TestCase):
    def test_post_working(self):
        """
        this test will pass the scenarios/list method
        """
        payload = {
            "token": test_token
        }

        output = requests.post(url, json=payload)

        expected_output = test_session_name
        assert output.json()['CM - Scale heat and cool density maps'][0]['session_name'] == expected_output

    def test_post_missing_parameter(self):
        """
        this test will fail because of missing parameters
        """
        payload = {
            "tokfadsfasden": test_token,
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_user_unidentified(self):
        """
        this test will fail because the used token is wrong
        """
        payload = {
            "token": 'toto',
        }

        output = requests.post(url, json=payload)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status
