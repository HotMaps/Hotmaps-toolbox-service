from unittest import TestCase
from .. import BASE_URL
import requests


class TestAskingPasswordRecovery(TestCase):
    def test_post_working(self):
        '''
        this test will ask for a user recovery
        '''
        url = BASE_URL + "/users/recovery/ask"

        payload = {
            "email": "hotmapstest@gmail.com"
        }

        output = requests.post(url, json=payload)

        expected_output = 'request for recovery successful'

        assert output.json()['message'] == expected_output

    def test_post_missing_parameter(self):
        '''
        this test will fail to activate a user because the parameters are not complete
        '''
        url = BASE_URL + "/users/recovery/ask"

        payload = {
            "youcantspellemail": "hotmapstest@gmail.com"
        }

        output = requests.post(url, json=payload)

        expected_output = '531'

        error_status = output.json()['error']['status']

        assert error_status == expected_output

    def test_user_not_existing(self):
        '''
        this test will fail to activate a user because the parameters are not complete
        '''
        url = BASE_URL + "/users/recovery/ask"

        payload = {
            "email": "hotmapstest2@gmail.com"
        }

        output = requests.post(url, json=payload)

        expected_output = 'request for recovery successful'

        assert output.json()['message'] == expected_output
