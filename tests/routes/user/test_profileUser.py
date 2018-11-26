import requests

from unittest import TestCase
from . import test_token


class TestProfileUser(TestCase):
    def test_post_working(self):
        """
        this test will pass the user/information method
        """
        url = "http://192.168.99.100/api/users/profile/update"
        test_last_name = 'toto'
        test_first_name = 'tata'
        payload = {
            "token": test_token,
            "last_name": test_last_name,
            "first_name": test_first_name
        }

        output = requests.post(url, json=payload)

        expected_output = 'User ' + test_last_name + ' ' + test_first_name + ' updated'

        assert output.json()['message'] == expected_output

    def test_post_missing_parameters(self):
        """
        this test will fail because of missing parameters
        """
        url = "http://192.168.99.100/api/users/profile/update"

        payload = {
            "tokentoto": test_token
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_user_unidentified(self):
        """
        this test will fail because of wrong user token
        """
        url = "http://192.168.99.100/api/users/profile/update"

        payload = {
            "token": "mybeautifultoken",
            "last_name": "toto",
            "first_name": 'tata'
        }

        output = requests.post(url, json=payload)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status

