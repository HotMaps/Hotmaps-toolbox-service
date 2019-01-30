import requests
import os
from unittest import TestCase
from . import BASE_URL, test_lau_heat_load

url = BASE_URL + "/upload/export/raster/nuts"


class TestExportRasterLau(TestCase):
    def test_post(self):
        """
        this test will pass the upload/export/raster/nuts method
        """
        payload = {
            "layers": "heat_tot_curr_density_lau2",
            "year": "2012",
            "nuts": ["AT90001"]
        }

        expected_output = float(os.path.getsize(test_lau_heat_load))

        output = requests.post(url, json=payload)

        assert len(output.content) == expected_output

    def test_port_wrong_parameters(self):
        """
        this test will fail because the wrong parameters are given
        """
        payload = {
            "laysdafers": "heat_tot_curr_density_lau2",
            "yegfdar": "2012",
            "nuts": ["AT90001"]
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_wrong_layer(self):
        """
        this test will fail because the layer is not a lau2 or nuts3
        """
        payload = {
            "layers": "heat_tot_curr_density_lau3",
            "year": "2012",
            "nuts": ["AT90001"]
        }

        output = requests.post(url, json=payload)

        expected_status = '532'

        assert output.json()['error']['status'] == expected_status
