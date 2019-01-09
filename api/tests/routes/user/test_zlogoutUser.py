import requests
from unittest import TestCase
from . import test_token
from .. import BASE_URL


# the z in the name is to run this test last to logout (but before the 2nd login that will change the valid token
class TestLogoutUser(TestCase):
    def test_post_work(self):
        '''
        This test will test that a user is correctly logout
        '''
        url = BASE_URL + "/users/logout"

        payload = {
            "token": test_token
        }

        output = requests.post(url, json=payload)

        expected_output = 'user disconnected'

        assert output.json()['message'] == expected_output

    def test_post_false_parameters(self):
        '''
        this test will fail to log in a user because the parameters are wrong
        '''
        url = BASE_URL + "/users/logout"

        payload = {
            "tokentoto": 'asdgsdgsdgsdaffds'
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_unidentified_user(self):
        '''
        this test will fail to log in a user because the user name is wrong
        '''
        url = BASE_URL + "/users/logout"

        payload = {
            "token": 'wowoosdifapsdgasd'
        }

        output = requests.post(url, json=payload)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status
