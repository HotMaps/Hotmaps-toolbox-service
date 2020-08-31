from unittest import TestCase

import requests

from . import BASE_URL

url = BASE_URL + '/upload/export/csv/nuts'


class TestExportCsvLau(TestCase):
    def test_post(self):
        """
        this test will pass the upload/export/csv/nuts method with lau input
        """
        payload = {
            'layers': 'wwtp_capacity_lau2',
            'year': '2012',
            'schema': 'public',
            'nuts': ['AT30639']
        }

        expected_status = 200

        output = requests.post(url, json=payload)

        assert output.status_code == expected_status

    def test_port_wrong_parameters(self):
        """
        this test will fail because the wrong parameters are given
        """
        payload = {
            'fdslayers': 'wwtp_capacity_lau2',
            'ydfsear': '2012',
            'scfdsahema': 'public',
            'nuts': ['AT30639']
            }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    # This no longer applies (LAU1 is not used anymore and CSV can be exported up to NUTS2 level)
    # def test_post_huge_request(self):
    #     """
    #     this test will pass the upload/export/csv/hectare method
    #     """
    #     payload = {
    #         "layers": "wwtp_capacity_lau1",
    #         "year": "2012",
    #         "schema": "public",
    #         "nuts": ["AT30639"]
    #     }

    #     output = requests.post(url, json=payload)

    #     expected_status = '532'

    #     assert output.json()['error']['status'] == expected_status