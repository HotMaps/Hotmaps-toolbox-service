import requests
from unittest import TestCase
from . import BASE_URL, test_token, test_csv_file

url = BASE_URL + "/upload/csv"


class TestCsv(TestCase):
    def test_post_working(self):
        """
        this test will pass the upload/csv method
        """
        list_url = BASE_URL + "/upload/list"
        payload = {
            "token": test_token,
        }

        output = requests.post(list_url, json=payload)
        test_upload_id = output.json()['uploads'][0]['id']

        complete_url = url + '/' + str(test_token) + '/' + str(test_upload_id)
        output = requests.get(complete_url)

        expected_output = "name, size\r\ntest, 10"

        assert output.content == expected_output

    def test_csv_user_unidentified(self):
        """
        this test will pass the uploads/add method
        """
        complete_url = url + '/' + str("HelloFromToken") + '/' + str(-5)

        output = requests.get(complete_url)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status

    def test_csv_upload_not_existing(self):
        """
        this test will pass the uploads/add method
        """

        complete_url = url + '/' + str(test_token) + '/' + str(-5)

        output = requests.get(complete_url)

        expected_status = '543'

        assert output.json()['error']['status'] == expected_status

