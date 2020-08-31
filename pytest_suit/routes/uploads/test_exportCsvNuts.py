from unittest import TestCase

import requests

from . import BASE_URL

url = BASE_URL + '/upload/export/csv/nuts'


class TestExportCsvNuts(TestCase):
    def test_post(self):
        """
        this test will pass the upload/export/csv/nuts method with lau input
        """
        payload = {
            'layers': 'wwtp_capacity_nuts3',
            'year': '2012',
            'schema': 'public',
            'nuts': ['FR102']
        }

        expected_status = 200

        output = requests.post(url, json=payload)

        assert output.status_code == expected_status

    def test_port_wrong_parameters(self):
        """
        this test will fail because the wrong parameters are given
        """
        payload = {
            'fdslayers': 'wwtp_capacity_nuts3',
            'ydfsear': '2012',
            'scfdsahema': 'public',
            'nuts': ['AT127']
            }

        output = requests.post(url, json=payload)

        expected_status = '531'

        assert output.json()['error']['status'] == expected_status

    # This no longer applies (CSV can be exported up to NUTS2 level and even NUTS0 in some cases)
    # def test_post_huge_request(self):
    #     """
    #     this test will fail because the given layer is not correct
    #     """
    #     payload = {
    #         "layers": "wwtp_capacity_nuts0",
    #         "year": "2012",
    #         "schema": "public",
    #         "nuts": ["FR"]
    #     }

    #     output = requests.post(url, json=payload)

    #     expected_status = '532'

    #     assert output.json()['error']['status'] == expected_status