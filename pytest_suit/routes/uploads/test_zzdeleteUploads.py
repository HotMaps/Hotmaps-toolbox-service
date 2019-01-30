import requests

from unittest import TestCase
from . import test_token, BASE_URL

url = BASE_URL + "/upload/delete"


class TestDeleteUploads(TestCase):
    def test_delete_working(self):
        """
        this test will pass the uploads/remove method
        """
        list_url = BASE_URL + "/upload/list"
        payload = {
            "token": test_token,
        }

        output = requests.post(list_url, json=payload)
        test_upload_id = output.json()['uploads'][0]['id']

        payload = {
            "id": test_upload_id,
            "token": test_token,
        }

        output = requests.delete(url, json=payload)

        expected_output = 'Upload deleted'
        assert output.json()['message'] == expected_output

    def test_delete_missing_parameter(self):
        """
        this test will fail because the given parameters are wrong
        """
        payload = {
            "etsid": -5,
            "togfdken": test_token,
        }

        output = requests.delete(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_delete_user_unidentified(self):
        """
        this test will fail because the user is not connected
        """
        payload = {
            "id": -5,
            "token": "ThisIsAWrongToken",
        }

        output = requests.delete(url, json=payload)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status

    def test_delete_upload_not_existing(self):
        """
        this test will fail because the upload does not exists
        """
        payload = {
            "id": -5,
            "token": test_token,
        }

        output = requests.delete(url, json=payload)

        expected_status = '543'

        assert output.json()['error']['status'] == expected_status

