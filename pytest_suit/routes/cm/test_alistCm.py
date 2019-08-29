import requests

from unittest import TestCase
from . import BASE_URL, test_cm_id

url = BASE_URL + '/cm/list'


class TestListCM(TestCase):
    def test_post_working_with_cm(self):
        """
        this test will pass the cm/list method with a cm in the db
        """

        output = requests.post(url)

        expected_output = test_cm_id
        assert output.json()[0]['cm_id'] == expected_output

# TODO test when there are no cm registered
