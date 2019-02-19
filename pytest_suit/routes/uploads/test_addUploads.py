import requests

from unittest import TestCase
from . import BASE_URL, test_token, test_csv_file, test_upload_name
from ..user.test_profileUser import test_first_name

url = BASE_URL + '/upload/add'


class TestAddUploads(TestCase):
    def test_post_working(self):
        """
        this test will pass the uploads/add method
        """
        files = {'file': open(test_csv_file, 'rb')}
        values = {'token': test_token, 'name': test_upload_name}

        output = requests.post(url, files=files, data=values)

        expected_output = 'file ' + test_upload_name + ' added for the user ' + test_first_name
        assert output.json()['message'] == expected_output

    def test_post_missing_parameter(self):
        """
        this test will fail because of missing parameters
        """
        files = {'file': open(test_csv_file, 'rb')}
        values = {'dstoken': test_token, 'sdafname': test_upload_name}

        output = requests.post(url, files=files, data=values)

        expected_output = 'Input payload validation failed'
        assert output.json()['message'] == expected_output

    def test_post_user_unidentified(self):
        """
        this test will fail because the used token is wrong
        """
        files = {'file': open(test_csv_file, 'rb')}
        values = {'token': 'invalidtoken', 'name': test_upload_name}

        output = requests.post(url, files=files, data=values)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status
