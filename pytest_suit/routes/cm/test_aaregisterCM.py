import requests

from unittest import TestCase
from . import BASE_URL, test_cm_id

url = BASE_URL + '/cm/register'


class TestListCM(TestCase):
    def test_post_working(self):
        """
        this test will pass the cm/register
        """

        signature_cm = {}

        output = requests.post(url)

        expected_output = []
        assert output.json() == expected_output

    def test_post_working_with_cm(self):
        """
        this test will pass the cm/list method with no cm in the db
        """

        signature_cm = {}

        output = requests.post(url)

        expected_output = []
        assert output.json() == expected_output
