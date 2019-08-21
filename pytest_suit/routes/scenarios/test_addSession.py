import requests

from unittest import TestCase
from . import BASE_URL, test_token, test_session_name

url = BASE_URL + '/scenarios/add'


class TestAddSession(TestCase):
    def test_post_working(self):
        """
        this test will pass the scenarios/add method
        """

        payload = {
            "front" : {
                "token": test_token,
                "name_session": test_session_name
            },
            "cm" : {
                "name": "CM - Scale heat and cool density maps",
                "indicator": [{
                    "name": "Test indicator",
                    "unit": "kWh",
                    "value": "1532.7"
                }]
            }
        }

        output = requests.post(url, json=payload)

        expected_output = 'session created successfully'

        assert output.json()['message'] == expected_output

    def test_post_missing_parameter(self):
        """
        this test will fail because of missing parameters
        """

        payload = {
            "front" : {
                "twdeoken": test_token,
                "name_sesswedion": test_session_name
            },
            "cm" : {
                "name": "CM - Scale heat and cool density maps",
                "indicator": [{
                    "name": "Test indicator",
                    "unit": "kWh",
                    "value": "1532.7"
                }]
            }
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_user_unidentified(self):
        """
        this test will fail because the used token is wrong
        """
        payload = {
            "front" : {
                "token": "toto",
                "name_session": test_session_name
            },
            "cm" : {
                "name": "CM - Scale heat and cool density maps",
                "indicator": [{
                    "name": "Test indicator",
                    "unit": "kWh",
                    "value": "1532.7"
                }]
            }
        }

        output = requests.post(url, json=payload)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status
