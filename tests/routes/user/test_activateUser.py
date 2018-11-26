from unittest import TestCase
from .. import BASE_URL
import requests


class TestActivateUser(TestCase):
    # The working method test has been removed, because the user is not deleted each time and deleting a user is
    # not currently implemented, deleting it manually could lead to a security issue that we wanted to avoid
    def test_post_missing_parameter(self):
        '''
        this test will fail to activate a user because the parameters are not complete
        '''
        url = BASE_URL + "/users/register/activate"

        payload = {
            "tokentoto": "did you really expected it to work ?"
        }

        output = requests.post(url, json=payload)

        expected_output = '531'

        error_status = output.json()['error']['status']

        assert error_status == expected_output

    def test_post_invalid_token(self):
        '''
        this test will fail to activate a user because the parameters are not complete
        '''
        url = BASE_URL + "/users/register/activate"

        payload = {
            "token": "did you really expected it to work ?"
        }

        output = requests.post(url, json=payload)

        expected_output = '536'

        error_status = output.json()['error']['status']

        assert error_status == expected_output
