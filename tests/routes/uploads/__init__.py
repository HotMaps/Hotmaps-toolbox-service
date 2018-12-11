from .. import BASE_URL
from ..user import test_token
import os
dirname = os.path.dirname(__file__)
test_base_file = os.path.join(dirname, 'test_upload.tif')
test_size = float(os.path.getsize(test_base_file)) / 1000000