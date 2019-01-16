import requests

from unittest import TestCase
from . import BASE_URL, test_token, test_csv_file, test_csv_name, test_upload_name
from ..user.test_profileUser import test_first_name

url = BASE_URL + '/upload/add?file_name=' + test_csv_name + '&token =' + test_token


class TestAddUploads(TestCase):
    def test_post_working(self):
        """
        this test will pass the uploads/add method
        """
        files = {'file': open(test_csv_file, 'rb')}
        values = {'token': test_token, 'upload_name': test_upload_name}

        output = requests.post(url, files=files, data=values)

        expected_output = 'file ' + test_csv_name + ' added for the user ' + test_first_name
        assert output.json()['message'] == expected_output

    def test_post_missing_parameter(self):
        """
        this test will fail because of missing parameters
        """
        files = {'file': open(test_csv_file, 'rb')}
        values = {'dstoken': test_token}

        output = requests.post(url, files=files, data=values)

        expected_output = 'Input payload validation failed'
        assert output.json()['message'] == expected_output

    def test_post_user_unidentified(self):
        """
        this test will fail because the used token is wrong
        """
        files = {'file': open(test_csv_file, 'rb')}
        values = {'token': 'invalidtoken', 'upload_name': test_upload_name}

        output = requests.post(url, files=files, data=values)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status

    def test_post_z_already_existing_url(self):  # the z in the name is used to run the test last
        """
        this test will fail because the file url is already existing
        """
        files = {'file': open(test_csv_file, 'rb')}
        values = {'token': test_token, 'upload_name': test_upload_name}

        output = requests.post(url, files=files, data=values)

        expected_status = '541'

        assert output.json()['error']['status'] == expected_status
