# import requests
#
# from unittest import TestCase
# from . import test_token, BASE_URL
# from .test_addUploads import test_file_name
#
# url = BASE_URL + "/upload/remove_upload"
#
#
# class TestDeleteUploads(TestCase):
#     def test_delete_working(self):
#         """
#         this test will pass the uploads/remove method
#         """
#         payload = {
#             "url": test_file_name,
#             "token": test_token,
#         }
#
#         output = requests.delete(url, json=payload)
#
#         expected_output = 'Upload removed'
#         assert output.json()['message'] == expected_output
#
#     def test_delete_missing_parameter(self):
#         """
#         this test will fail because the given parameters are wrong
#         """
#         payload = {
#             "usafrl": test_file_name,
#             "togfdken": test_token,
#         }
#
#         output = requests.delete(url, json=payload)
#
#         expected_status = '531'
#
#         assert output.json()['error']['status'] == expected_status
#
#     def test_delete_user_unidentified(self):
#         """
#         this test will pass the uploads/add method
#         """
#         payload = {
#             "url": test_file_name,
#             "token": "ThisIsAWrongToken",
#         }
#
#         output = requests.delete(url, json=payload)
#
#         expected_status = '539'
#
#         assert output.json()['error']['status'] == expected_status
#
#     def test_delete_user_not_owner(self):
#         """
#         this test will pass the uploads/add method
#         """
#         payload = {
#             "url": "testForUnitTesting",
#             "token": test_token,
#         }
#
#         output = requests.delete(url, json=payload)
#
#         expected_status = '540'
#
#         assert output.json()['error']['status'] == expected_status
#
#     def test_delete_upload_not_existing(self):
#         """
#         this test will pass the uploads/add method
#         """
#         payload = {
#             "url": "thisisarandomurl",
#             "token": test_token,
#         }
#
#         output = requests.delete(url, json=payload)
#
#         expected_status = '543'
#
#         assert output.json()['error']['status'] == expected_status
#
