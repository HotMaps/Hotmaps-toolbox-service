from unittest import TestCase

import requests
import os
import subprocess

from . import BASE_URL, test_uuid, test_tif_file

url = BASE_URL + "/upload/export/cmLayer"


class TestExportCMLayer(TestCase):
    def test_post(self):
        """
        this test will pass the upload/export/cmLayer method
        """
        payload = {
            "uuid": test_uuid,
            "type": "raster",
        }

        path = '/tmp/' + test_uuid + '.tif'
        with open(path, 'x') as f:
            expected_status = 200
            output = requests.post(url, json=payload)
            assert output.status_code == expected_status

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
