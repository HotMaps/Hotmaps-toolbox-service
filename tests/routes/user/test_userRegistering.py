from unittest import TestCase
from .. import BASE_URL
import requests


class TestUserRegistering(TestCase):
    # The working method test has been removed, because the user is not deleted each time and deleting a user is
    # not currently implemented, deleting it manually could lead to a security issue that we wanted to avoid
    def test_post_user_already_existing(self):
        '''
        this test will fail to register a new user because the user is already created
        '''
        url = BASE_URL + "/users/register"

        payload = {
            "password": "this",
            "first_name": "is",
            "last_name": "a",
            "email": "hotmapstest@gmail.com"
        }

        output = requests.post(url, json=payload)

        expected_output = '535'

        error_status = output.json()['error']['status']

        assert error_status == expected_output

    def test_post_false_parameters(self):
        '''
        this test will fail to register a new user because the parameters are not complete
        '''
        url = BASE_URL + "/users/register"

        payload = {
            "passwordfds": "this",
            "first_gsfdname": "is",
            "lasfdst_name": "a",
            "dfsemail": "hotmapstest@gmail.com"
        }

        output = requests.post(url, json=payload)

        expected_output = '531'

        error_status = output.json()['error']['status']

        assert error_status == expected_output
