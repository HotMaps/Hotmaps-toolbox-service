from api.app.api_v1.scenarios import save_session

from unittest import TestCase
from . import BASE_URL, test_token, test_session_name



class TestAddSession(TestCase):
    def test_post_working(self):
        """
        this test will pass the scenarios/add method
        """

        payload_front = {
            "token": test_token,
            "name_session": test_session_name
        }
        response_cm = {
            "name": "CM - Scale heat and cool density maps",
            "indicator": [{
                "name": "Test indicator",
                "unit": "kWh",
                "value": "1532.7"
            }]
        }

        output = save_session(payload_front, response_cm)

        expected_output = 'session created successfully'

        assert output.json()['message'] == expected_output

    def test_post_missing_parameter(self):
        """
        this test will fail because of missing parameters
        """
        payload_front = {
            "token": test_token,
            "name_session": test_session_name
        }
        response_cm = {
            "nawerme": "CM - Scale heat and cool density maps",
            "indicator": [{
                "name": "Test indicator",
                "unit": "kWh",
                "value": "1532.7"
            }]
        }

        output = save_session(payload_front, response_cm)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_user_unidentified(self):
        """
        this test will fail because the used token is wrong
        """
        payload_front = {
            "token": "toto",
            "name_session": test_session_name
        }
        response_cm = {
            "name": "CM - Scale heat and cool density maps",
            "indicator": [{
                "name": "Test indicator",
                "unit": "kWh",
                "value": "1532.7"
            }]
        }

        output = save_session(payload_front, response_cm)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status
