from flask_restplus import reqparse
import werkzeug

pagination_arguments = reqparse.RequestParser()
pagination_arguments.add_argument('page', type=int, required=False, default=1, help='Page number')
pagination_arguments.add_argument('bool', type=bool,  required=False, default=1, help='Page number')
pagination_arguments.add_argument('per_page', type=int, required=False, choices=[2, 10, 20, 30, 40, 50],
                                  default=10, help='Results per page {error_msg}')

file_upload = reqparse.RequestParser()
file_upload.add_argument('token', type=str, required=True, help='Login token')
file_upload.add_argument('layer', type=str, required=False, help='file layer')
file_upload.add_argument('name', type=str, required=True, help='upload name')
file_upload.add_argument('file',
                         type=werkzeug.datastructures.FileStorage,
                         location='files',
                         required=True,
                         help='file')
