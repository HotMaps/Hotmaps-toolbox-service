import requests
import os
from unittest import TestCase
from . import BASE_URL, test_hectare_heat_load

url = BASE_URL + "/upload/export/raster/hectare"


class TestExportRasterHectare(TestCase):
    def test_post(self):
        """
        this test will pass the upload/export/csv/hectare method
        """
        payload = {
            "layers": "heat_tot_curr_density_ha",
            "year": "2012",
            "areas": [{
                "points":   [
                    {"lat": 48.25759852914997, "lng": 16.351432800292972},
                    {"lat": 48.267426453675895, "lng": 16.351432800292972},
                    {"lat": 48.267426453675895, "lng": 16.369628906250004},
                    {"lat": 48.25759852914997, "lng": 16.369628906250004}
                ]}
            ]
        }

        expected_output = float(os.path.getsize(test_hectare_heat_load))

        output = requests.post(url, json=payload)

        assert len(output.content) == expected_output

    def test_port_wrong_parameters(self):
        """
        this test will fail because the wrong parameters are given
        """
        payload = {
            "lfdsaayers": "heat_tot_curr_density_ha",
            "yefsdaar": "2012",
            "aregfas": [{
                "points":   [
                    {"lat": 48.25759852914997, "lng": 16.351432800292972},
                    {"lat": 48.267426453675895, "lng": 16.351432800292972},
                    {"lat": 48.267426453675895, "lng": 16.369628906250004},
                    {"lat": 48.25759852914997, "lng": 16.369628906250004}
                ]}
            ]
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_wrong_layer(self):
        """
        this test will fail because the layer is not corresponding to hectare
        """
        payload = {
            "layers": "heat_tot_curr_density_ha2",
            "year": "2012",
            "areas": [{
                "points":   [
                    {"lat": 48.25759852914997, "lng": 16.351432800292972},
                    {"lat": 48.267426453675895, "lng": 16.351432800292972},
                    {"lat": 48.267426453675895, "lng": 16.369628906250004},
                    {"lat": 48.25759852914997, "lng": 16.369628906250004}
                ]}
            ]
        }

        output = requests.post(url, json=payload)

        expected_status = '530'

        assert output.json()['error']['status'] == expected_status
