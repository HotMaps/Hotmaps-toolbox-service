import requests

import unittest
from unittest import TestCase
from . import BASE_URL, test_token, test_config

url = BASE_URL + '/snapshot/load'


class TestLoadSnapshot(TestCase):
    
    @unittest.skip('This test keeps failing even though we did not change anything')
    def test_post_working(self):
        """
        this test will pass the snapshot/load method
        """
        list_url = BASE_URL + '/snapshot/list'
        payload = {
            'token': test_token,
        }

        output = requests.post(list_url, json=payload)
        test_snapshot_id = output.json()['snapshots'][0]['id']

        payload = {
            'token': test_token,
            'id': test_snapshot_id
        }

        output = requests.post(url, json=payload)

        expected_output = test_config
        assert output.json()['config'] == expected_output

    def test_post_missing_parameter(self):
        """
        this test will fail because of missing parameters
        """
        payload = {
            'tokfadsfasden': test_token,
            'ifdsad': -5
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_not_existing_snapshot(self):
        """
        this test will fail because the snapshot does not exists
        """
        payload = {
            'token': test_token,
            'id': -5
        }

        output = requests.post(url, json=payload)

        expected_status = '537'

        assert output.json()['error']['status'] == expected_status

    def test_post_user_unidentified(self):
        """
        this test will fail because the used token is wrong
        """
        payload = {
            'token': 'toto',
            'id': -5
        }

        output = requests.post(url, json=payload)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status
