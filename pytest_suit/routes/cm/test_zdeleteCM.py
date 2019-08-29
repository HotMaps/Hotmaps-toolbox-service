import requests

from unittest import TestCase
from . import BASE_URL, test_cm_id

url = BASE_URL + '/cm/delete'


class TestDeleteCM(TestCase):
    def test_delete_working(self):
        """
        this test will pass the cm/delete method
        """
        list_url = BASE_URL + "/cm/list"

        output = requests.post(list_url)
        test_id = output.json()[0]["cm_id"]

        payload = { 'cm_id': test_id }
        output = requests.delete(url, json=payload)

        expected_output = 'CM removed'
        assert output.json()['message'] == expected_output

    def test_delete_missing_parameter(self):
        """
        this test will fail because the given parameters are wrong
        """
        payload = {
            "idfwsfd": test_cm_id
        }

        output = requests.delete(url, json=payload)

        expected_status = '531'

        assert output.json() == expected_status


    def test_delete_upload_not_existing(self):
        """
        this test will fail because the cm does not exists
        """
        payload = {
            "id": -5
        }

        output = requests.delete(url, json=payload)

        expected_status = '545'

        assert output.json() == expected_status
