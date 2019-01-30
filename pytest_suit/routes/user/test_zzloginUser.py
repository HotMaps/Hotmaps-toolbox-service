import requests
from unittest import TestCase
from .. import BASE_URL


# we need to run the second login after logging out as the token will be changed
class TestLoginUser(TestCase):

    def test_post_working(self):
        '''
        this test will log in the user
        '''
        url = BASE_URL + "/users/login"

        payload = {
            "email": "hotmapstest@gmail.com",
            "password": "weqriogvyx"
        }

        output = requests.post(url, json=payload)

        expected_output = 'user connected'

        assert output.json()['message'] == expected_output

    def test_post_false_parameters(self):
        '''
        this test will fail to log in a user because the parameters are wrong
        '''
        url = BASE_URL + "/users/login"

        payload = {
            "emailsdaf": "hotmapstest@gmail.com",
            "passworgsadfdsad": "weqriogvyx"
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_false_username(self):
        '''
        this test will fail to log in a user because the user name is wrong
        '''
        url = BASE_URL + "/users/login"

        payload = {
            "email": "notme@gmail.com",
            "password": "batman1234"
        }

        output = requests.post(url, json=payload)

        expected_status = '538'

        assert output.json()['error']['status'] == expected_status

    def test_post_false_password(self):
        '''
        this test will fail to log in a user because the user password is wrong
        '''
        url = BASE_URL + "/users/login"

        payload = {
            "email": "hotmapstest@gmail.com",
            "password": "batman1234"
        }

        output = requests.post(url, json=payload)

        expected_status = '538'

        assert output.json()['error']['status'] == expected_status
