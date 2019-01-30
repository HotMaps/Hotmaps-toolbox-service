from .. import BASE_URL
import os
dirname = os.path.dirname(__file__)

test_csv_file = os.path.join(dirname, 'test_assets/test.csv')
test_csv_size = float(os.path.getsize(test_csv_file)) / 1000000
test_csv_name = 'test.csv'

test_hectare_wwtp = os.path.join(dirname, 'test_assets/test_export_wwtp_hectare.csv')
test_lau_wwtp = os.path.join(dirname, 'test_assets/test_export_wwtp_lau.csv')
test_nuts_wwtp = os.path.join(dirname, 'test_assets/test_export_wwtp_nuts.csv')

test_hectare_heat_load = os.path.join(dirname, 'test_assets/test_hectare_heat_load.tif')
test_lau_heat_load = os.path.join(dirname, 'test_assets/test_lau_heat_load.tif')
test_nuts_heat_load = os.path.join(dirname, 'test_assets/test_nuts_heat_load.tif')