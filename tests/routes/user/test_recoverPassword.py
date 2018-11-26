import requests
from unittest import TestCase


class TestRecoverPassword(TestCase):
    def test_post_parameter_wrong(self):
        '''
        This test will fail to recover the password because the parameters are wrong
        '''
        url = "http://192.168.99.100/api/users/recovery"

        payload = {
            "tokentoto": "thisismynicetoken",
            "passwordword": "nottoday"
        }

        output = requests.post(url, json=payload)

        expected_output = '531'

        error_status = output.json()['error']['status']
        assert error_status == expected_output


    def test_post_wrong_token(self):
        '''
        This test will fail to recover the password because the token is wrong
        '''
        url = "http://192.168.99.100/api/users/recovery"

        payload = {
            "token": "thisismynicetoken",
            "password": "nottoday"
        }

        output = requests.post(url, json=payload)

        expected_output = '536'

        error_status = output.json()['error']['status']
        assert error_status == expected_output