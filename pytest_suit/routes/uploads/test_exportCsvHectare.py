from unittest import TestCase

import requests

from . import BASE_URL

url = BASE_URL + '/upload/export/csv/hectare'


class TestExportCsvHectare(TestCase):
    def test_post_wwtp_power(self):
        """
        this test will pass the upload/export/csv/hectare method
        """
        payload = {
            'layers': 'wwtp_power_ha',
            'year': '2012',
            'schema': 'public',
            'areas': [{
                'points':
                [
                    {'lat': 48.0294274293825, 'lng': 16.29178047180176},
                    {'lat': 48.03674530430821, 'lng': 16.29178047180176},
                    {'lat': 48.03674530430821, 'lng': 16.31229400634766},
                    {'lat': 48.0294274293825, 'lng': 16.31229400634766}
                ]
            }]
        }

        expected_status = 200

        output = requests.post(url, json=payload)

        assert output.status_code == expected_status

    def test_post_wwtp_capacity(self):
        """
        this test will pass the upload/export/csv/hectare method
        """
        payload = {
            'layers': 'wwtp_capacity_ha',
            'year': '2012',
            'schema': 'public',
            'areas': [{
                'points':
                [
                    {'lat': 48.0294274293825, 'lng': 16.29178047180176},
                    {'lat': 48.03674530430821, 'lng': 16.29178047180176},
                    {'lat': 48.03674530430821, 'lng': 16.31229400634766},
                    {'lat': 48.0294274293825, 'lng': 16.31229400634766}
                ]
            }]
        }

        expected_status = 200

        output = requests.post(url, json=payload)

        assert output.status_code == expected_status

    def test_post_industrial_database_emissions(self):
        """
        this test will pass the upload/export/csv/hectare method
        """
        payload = {
            'layers': 'industrial_database_emissions_ha',
            'year': '2014',
            'schema': 'public',
            'areas': [{
                'points':
                [
                    {'lat':48.75075629617738,'lng':2.0764160156250004},
                    {'lat':49.005447494058096,'lng':2.0764160156250004},
                    {'lat':49.005447494058096,'lng':2.5048828125000004},
                    {'lat':48.75075629617738,'lng':2.5048828125000004}
                ]
            }]
        }

        expected_status = 200

        output = requests.post(url, json=payload)

        assert output.status_code == expected_status

    def test_post_industrial_database_subsector(self):
        """
        this test will pass the upload/export/csv/hectare method
        """
        payload = {
            'layers': 'industrial_database_subsector_ha',
            'year': '2014',
            'schema': 'public',
            'areas': [{
                'points':
                [
                    {'lat':48.75075629617738,'lng':2.0764160156250004},
                    {'lat':49.005447494058096,'lng':2.0764160156250004},
                    {'lat':49.005447494058096,'lng':2.5048828125000004},
                    {'lat':48.75075629617738,'lng':2.5048828125000004}
                ]
            }]
        }

        expected_status = 200

        output = requests.post(url, json=payload)

        assert output.status_code == expected_status

    def test_post_industrial_database_excess_heat(self):
        """
        this test will pass the upload/export/csv/hectare method
        """
        payload = {
            'layers': 'industrial_database_excess_heat_ha',
            'year': '2014',
            'schema': 'public',
            'areas': [{
                'points':
                [
                    {'lat':48.75075629617738,'lng':2.0764160156250004},
                    {'lat':49.005447494058096,'lng':2.0764160156250004},
                    {'lat':49.005447494058096,'lng':2.5048828125000004},
                    {'lat':48.75075629617738,'lng':2.5048828125000004}
                ]
            }]
        }

        expected_status = 200

        output = requests.post(url, json=payload)

        assert output.status_code == expected_status

    def test_port_wrong_parameters(self):
        """
        this test will fail because the wrong parameters are given
        """
        payload = {
            'fdslayers': 'wwtp_capacity_ha',
            'ydfsear': '2012',
            'scfdsahema': 'public',
            'arefdsas': [{
                'poinsts':
                    [
                        {'lat': 48.0294274293825, 'lng': 16.29178047180176},
                        {'lat': 48.03674530430821, 'lng': 16.29178047180176},
                        {'lat': 48.03674530430821, 'lng': 16.31229400634766},
                        {'lat': 48.0294274293825, 'lng': 16.31229400634766}
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
            'layers': 'wwtp_capacity_ha23',
            'year': '2012',
            'schema': 'public',
            'areas': [{
                'points':
                    [
                        {'lat': 48.0294274293825, 'lng': 16.29178047180176},
                        {'lat': 48.03674530430821, 'lng': 16.29178047180176},
                        {'lat': 48.03674530430821, 'lng': 16.31229400634766},
                        {'lat': 48.0294274293825, 'lng': 16.31229400634766}
                    ]
            }]
        }

        output = requests.post(url, json=payload)

        expected_status = '530'

        assert output.json()['error']['status'] == expected_status
