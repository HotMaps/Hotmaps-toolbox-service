import requests

from unittest import TestCase
from . import BASE_URL, test_cm_id

url = BASE_URL + '/cm/user-interface/'


class TestUserInterfaceCM(TestCase):
    def test_post_working_with_cm(self):
        """
        this test will pass the cm/user-interface method
        """

        payload = { 'cm_id': test_cm_id }

        output = requests.post(url, json=payload)

        expected_output = 'Multiplication factor'
        assert output.json()[0]['input_name'] == expected_output

    def test_post_cm_not_existing(self):
        """
        this test will fail because the cm does not exists
        """
        payload = {
            "cm_id": -5
        }

        output = requests.delete(url, json=payload)

        expected_status = '545'

        assert output.json() == expected_status
