from unittest import TestCase

import requests
import os

from . import BASE_URL, test_uuid

url = BASE_URL + "/upload/export/cmLayer"


class TestExportCMLayer(TestCase):
    def test_post(self):
        """
        this test will pass the upload/export/csv/hectare method
        """
        cmd = 'touch /var/tmp/' + test_uuid + '.tif'
        os.system(cmd)

        payload = {
            "uuid": test_uuid,
            "type": "raster",
        }

        expected_status = 200
        output = requests.post(url, json=payload)
        assert output.status_code == expected_status

        cmd = 'rm /var/tmp/' + test_uuid + '.tif'
        os.system(cmd)


    def test_port_wrong_parameters(self):
        """
        this test will fail because the wrong parameters are given
        """
        payload = {
            "uuuuuiiiid": test_uuid,
            "tyefepe": "raster",
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_wrong_layer(self):
        """
        this test will fail because the uuid does not exist
        """
        payload = {
            "uuid": "fake_uuid",
            "type": "raster"
        }

        output = requests.post(url, json=payload)

        expected_status = '541'

        assert output.json()['error']['status'] == expected_status
