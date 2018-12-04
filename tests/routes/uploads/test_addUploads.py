import requests

from unittest import TestCase
from . import BASE_URL
from . import test_token
from ..user.test_profileUser import test_first_name

url = BASE_URL + "/upload/add"
test_file_name = 'niceTestFile'
test_size = 40

class TestAddUploads(TestCase):
    def test_post_not_enough_space(self):
        """
        this test will pass the uploads/add method
        """

        payload = {
            "url": test_file_name,
            "file_name": test_file_name,
            "token": test_token,
            "size": test_size + 500
        }

        output = requests.post(url, json=payload)

        expected_status = '542'

        assert output.json()['error']['status'] == expected_status

    def test_post_working(self):
        """
        this test will pass the uploads/add method
        """
        payload = {
            "url": test_file_name,
            "file_name": test_file_name,
            "token": test_token,
            "size": test_size
        }

        output = requests.post(url, json=payload)

        expected_output = 'file ' + test_file_name + ' added for the user ' + test_first_name
        assert output.json()['message'] == expected_output

    def test_post_missing_parameter(self):
        """
        this test will fail because of missing parameters
        """
        payload = {
            "urdfsal": test_file_name,
            "filegsdf_name": test_file_name,
            "tokfdsen": test_token,
            "sigfsdze": test_size
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_user_unidentified(self):
        """
        this test will fail because the used token is wrong
        """
        payload = {
            "url": test_file_name,
            "file_name": test_file_name,
            "token": 'hey there',
            "size": test_size
        }

        output = requests.post(url, json=payload)

        expected_status = '539'

        assert output.json()['error']['status'] == expected_status

    def test_post_z_already_existing_url(self):  # the z in the name is used to run the test last
        """
        this test will fail because the file url is already existing
        """
        payload = {
            "url": test_file_name,
            "file_name": test_file_name,
            "token": test_token,
            "size": test_size
        }

        output = requests.post(url, json=payload)

        expected_status = '541'

        assert output.json()['error']['status'] == expected_status
