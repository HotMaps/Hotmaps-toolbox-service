import requests

from unittest import TestCase
from . import BASE_URL, test_tif_file_name, test_tif_file

url = BASE_URL + '/cm/files/<string:filename>'


class TestGetRasterFilesCM(TestCase):
    def test_post_working(self):
        """
        this test will pass the cm/files method
        """
        # cmd = "cp " + test_tif_file + " /var/tmp/"
        # os.system(cmd)
        #
        # output = requests.post(url, json=test_tif_file_name)
        #
        # expected_output = test_cm_id # TODO
        # assert output.json()[0]['cm_id'] == expected_output
        #
        # cmd = "rm /var/tmp/" + test_tif_file
        # os.system(cmd)
