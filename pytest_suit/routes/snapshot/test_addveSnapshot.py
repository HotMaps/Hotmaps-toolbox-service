import requests

from unittest import TestCase
from . import BASE_URL, test_token, test_config

url = BASE_URL + '/snapshot/add'


class TestAddSnapshot(TestCase):
    def test_post_working(self):
        """
        this test will pass the snapshot/add method
        """
        payload = {
            'token': test_token,
            'config': test_config
        }

        output = requests.post(url, json=payload)

        expected_output = 'snapshot created successfully'

        assert output.json()['message'] == expected_output

    def test_post_missing_parameter(self):
        """
        this test will fail because of missing parameters
        """
        payload = {
            'tokfadsfasden': test_token,
            'config': test_config
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_user_unidentified(self):
        """
        this test will fail because the used token is wrong
        """
        payload = {
            'token': 'toto',
            'config': test_config
        }

        output = requests.post(url, json=payload)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status
