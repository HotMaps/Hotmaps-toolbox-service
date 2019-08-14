from .. import BASE_URL, test_csv_file
from ..user import test_token
import uuid
import os

test_upload_name = 'pytest_upload_csv'
test_file = [f for f in os.listdir('/var/tmp') if f.endswith('.tif')][0]
test_uuid = test_file.replace('.tif', '')
