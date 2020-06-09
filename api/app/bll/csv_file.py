import shutil
import uuid
from io import StringIO

from ..api_v1.upload import get_csv_from_nuts, get_csv_from_hectare
from ..constants import UPLOAD_DIRECTORY


class ExportCut:
    @staticmethod
    def cut_nuts(layers: str, nuts: list, schema: str, year: str):
        """
        The method called to cut a given list of nuts into a csv
        :param layers: the layer selected
        :param nuts: the list of nuts to export
        :param schema: the DB schema
        :param year: the data year
        :return:
        """
        csv_result = get_csv_from_nuts(layers=layers, nuts=nuts, schema=schema, year=year)
        return save_file_csv_random_name(content=csv_result)

    @staticmethod
    def cut_hectares(areas: list, layers: str, schema: str, year: str):
        """
        The method called to cut a given selection of hectares into a csv
        :param areas: the area to cut
        :param layers: the layer to select
        :param schema: the DB schema
        :param year: the data_year
        :return:
        """
        csv_result = get_csv_from_hectare(areas=areas, layers=layers, schema=schema, year=year)
        return save_file_csv_random_name(content=csv_result)


def save_file_csv_random_name(content: StringIO):
    """
    Save a file into a temp folder with a random name
    :param content: the content of the file you want to write
    :return random_name: the name randomly generated
    """
    random_name = uuid.uuid4().hex + '.csv'
    path = UPLOAD_DIRECTORY + '/' + random_name
    content_str = content.getvalue()
    with open(path, 'w', encoding='utf8') as f:
        f.write(content_str)
    return path
