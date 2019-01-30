import requests
from unittest import TestCase
from . import BASE_URL, test_hectare_wwtp

url = BASE_URL + "/upload/export/csv/hectare"


class TestExportCsvHectare(TestCase):
    def test_post(self):
        """
        this test will pass the upload/export/csv/hectare method
        """
        payload = {
            "layers": "wwtp_capacity_ha",
            "year": "2012",
            "schema": "public",
            "areas": [{
                "points":
                [
                    {"lat": 48.1707794421798, "lng": 16.459751129150394},
                    {"lat": 48.17615986702756, "lng": 16.459751129150394},
                    {"lat": 48.17615986702756, "lng": 16.473655700683597},
                    {"lat": 48.1707794421798, "lng": 16.473655700683597}
                ]
            }]
        }

        expected_output_file = open(test_hectare_wwtp, "r")
        expected_output = expected_output_file.read()

        output = requests.post(url, json=payload)

        assert output.content == expected_output

    def test_port_wrong_parameters(self):
        """
        this test will fail because the wrong parameters are given
        """
        payload = {
            "fdslayers": "wwtp_capacity_ha",
            "ydfsear": "2012",
            "scfdsahema": "public",
            "arefdsas": [{
                "poinsts":
                    [
                        {"lat": 48.1707794421798, "lng": 16.459751129150394},
                        {"lat": 48.17615986702756, "lng": 16.459751129150394},
                        {"lat": 48.17615986702756, "lng": 16.473655700683597},
                        {"lat": 48.1707794421798, "lng": 16.473655700683597}
                    ]
            }]
        }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    def test_post_wrong_layer(self):
        """
        this test will fail because the layer is not corresponding to hectare
        """
        payload = {
            "layers": "wwtp_capacity_ha23",
            "year": "2012",
            "schema": "public",
            "areas": [{
                "points":
                    [
                        {"lat": 48.1707794421798, "lng": 16.459751129150394},
                        {"lat": 48.17615986702756, "lng": 16.459751129150394},
                        {"lat": 48.17615986702756, "lng": 16.473655700683597},
                        {"lat": 48.1707794421798, "lng": 16.473655700683597}
                    ]
            }]
        }

        output = requests.post(url, json=payload)

        expected_status = '530'

        assert output.json()['error']['status'] == expected_status
