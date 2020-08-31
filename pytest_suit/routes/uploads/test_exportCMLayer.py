from unittest import TestCase

import requests

from . import BASE_URL, test_export_cm_layer_uuid, test_tif_file
import os

url = BASE_URL + '/upload/export/cmLayer'


class TestExportCMLayer(TestCase):
    def test_post(self):
        """
        this test will pass the upload/export/cmLayer method
        """
        cmd = 'cp ' + test_tif_file + ' /var/tmp/'
        os.system(cmd)

        payload = {
            'uuid': test_export_cm_layer_uuid,
            'type': 'raster',
        }

        expected_status = 200
        output = requests.post(url, json=payload)
        assert output.status_code == expected_status

        cmd = 'rm /var/tmp/' + test_export_cm_layer_uuid + '.tif'
        os.system(cmd)

    def test_port_wrong_parameters(self):
        """
        this test will fail because the wrong parameters are given
        """
        payload = {
            'uuuuuiiiid': test_export_cm_layer_uuid,
            'tyefepe': 'raster',
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_wrong_layer(self):
        """
        this test will fail because the uuid does not exist
        """
        payload = {
            'uuid': 'fake_uuid',
            'type': 'raster'
        }

        output = requests.post(url, json=payload)

        expected_status = '541'

        assert output.json()['error']['status'] == expected_status
