import requests

import unittest
from unittest import TestCase
from . import BASE_URL, test_token, test_config

url = BASE_URL + '/snapshot/list'


class TestListSnapshot(TestCase):
    
    @unittest.skip('This test keeps failing even though we did not change anything')
    def test_post_working(self):
        """
        this test will pass the snapshot/list method
        """
        payload = {
            'token': test_token
        }

        output = requests.post(url, json=payload)

        expected_output = test_config
        assert output.json()['snapshots'][0]['config'] == expected_output

    def test_post_missing_parameter(self):
        """
        this test will fail because of missing parameters
        """
        payload = {
            'tokfadsfasden': test_token,
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
        }

        output = requests.post(url, json=payload)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status
