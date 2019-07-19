import requests

from unittest import TestCase
from . import BASE_URL, test_token, test_config

url = BASE_URL + '/scenarios/delete'


class TestDeleteSnapshot(TestCase):
    def test_delete_working(self):
        """
        this test will pass the scenarios/delete method
        """
        list_url = BASE_URL + "/scenarios/delete"
        payload = {
            "token": test_token,
        }

        output = requests.post(list_url, json=payload)
        test_scenario_id = output.json()['scenarios'][0]['id']

        payload = {
            "token": test_token,
            "id": test_scenario_id,
        }

        output = requests.delete(url, json=payload)

        expected_output = "The session has been deleted"

        assert output.json()['message'] == expected_output

    def test_delete_missing_parameter(self):
        """
        this test will fail because of missing parameters
        """
        payload = {
            "tokfadsfasden": test_token,
            "ifdsad": -5
        }

        output = requests.delete(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_delete_not_existing_snapshot(self):
        """
        this test will fail because the session does not exists
        """
        payload = {
            "token": test_token,
            "id": -5
        }

        output = requests.delete(url, json=payload)

        expected_status = '537'

        assert output.json()['error']['status'] == expected_status

    def test_delete_user_unidentified(self):
        """
        this test will fail because the used token is wrong
        """
        payload = {
            "token": 'toto',
            "id": -5
        }

        output = requests.delete(url, json=payload)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status
