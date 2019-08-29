import requests

from unittest import TestCase
from . import BASE_URL, signature_cm

url = BASE_URL + '/cm/register/'


class TestRegisterCM(TestCase):
    def test_post_working(self):
        """
        this test will pass the cm/register
        """

        output = requests.post(url, json=signature_cm)

        expected_output = "The CM 10 has been registered"
        assert output.json() == expected_output


    def test_post_missing_parameter(self):
        """
        this test will does not pass the cm/register because of missing parameters
        """

        output = requests.post(url, json={})

        expected_output = "all parameters are missing"
        assert output.json()['message'] == expected_output
