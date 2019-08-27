import requests

from unittest import TestCase
from . import BASE_URL, test_cm_id

url = BASE_URL + '/cm/delete'


class TestListCM(TestCase):
    def test_delete_working(self):
        """
        this test will pass the uploads/remove method
        """
        list_url = BASE_URL + "/cm/list"

        output = requests.post(list_url, json=payload)

        # should be the file added in add 'test_addUploads.py'
        test = output.json()['cm'][0]["id"] #TODO: to verify

        payload = {
            "id": test
        }

        output = requests.delete(url, json=payload)

        expected_output = 'CM removed' #TODO: to modify
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
        this test will fail because the upload does not exists
        """
        payload = {
            "id": -5
        }

        output = requests.delete(url, json=payload)

        expected_status = '546'

        assert output.json() == expected_status
