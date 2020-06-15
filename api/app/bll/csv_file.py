import os
import uuid
from io import StringIO

from ..api_v1.upload import get_csv_from_nuts, get_csv_from_hectare
from ..constants import UPLOAD_DIRECTORY
from .. import model
from ..helper import write_wkt_csv, area_to_geom, generate_csv_name, projection_4326_to_3035


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
        return ExportCut.save_file_csv_random_name(content=csv_result)

    @staticmethod
    def cut_personal_layer(scale_level, upload_url, areas):
        """
        The method called to cut a given list of nuts or a selection into a csv for a presonal layer
        :param scale_level: nuts, lau or hectare
        :param upload_url: the URL of the selected personal layer
        :param areas: the selection on the map
        :return:
        """
        if scale_level == 'hectare':
            areas = area_to_geom(areas)
            cutline_input = write_wkt_csv(generate_csv_name(UPLOAD_DIRECTORY), projection_4326_to_3035(areas))
        else:
            cutline_input = model.get_shapefile_from_selection(scale_level, areas, UPLOAD_DIRECTORY)

        cmd_cutline, output_csv = ExportCut.temp_prepare_clip_personal_layer(cutline_input, upload_url)
        args = model.commands_in_array(cmd_cutline)
        model.run_command(args)
        if not os.path.isfile(output_csv):
            return {
                "message": "not a csv file"
            }
        return {
            "path": output_csv
        }

    @staticmethod
    def temp_prepare_clip_personal_layer(cutline_input, upload_url):
        """
        Helper method to clip a personal layer
        :param cutline_input:
        :param upload_url: the url of the upload
        :return: a tuple containing the command to use later ant the output csv path
        """
        upload_url += "data.csv"
        output_csv = generate_csv_name(UPLOAD_DIRECTORY)
        cmd_cutline = "ogr2ogr -f 'CSV' -clipsrc {} {} {} -oo GEOM_POSSIBLE_NAMES=geometry_wkt -oo KEEP_GEOM_COLUMNS=NO".format(
            cutline_input, output_csv, upload_url)
        return cmd_cutline, output_csv

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
        return ExportCut.save_file_csv_random_name(content=csv_result)

    @staticmethod
    def save_file_csv_random_name(content: StringIO):
        """
        Save a file into a temp folder with a random name
        :param content: the content of the file you want to write
        :return random_name: the name randomly generated
        """
        path = ExportCut.generate_random_file_name()
        content_str = content.getvalue()
        with open(path, 'w', encoding='utf8') as f:
            f.write(content_str)
        return path

    @staticmethod
    def generate_random_file_name(extension: str = '.csv'):
        """
        generate a random file name
        :param extension: the extension of the file, default to .csv
        :return: the path of the generated file name or None if extension doesn't start with a dot
        """
        # the extension must be an extension
        if not extension.startswith('.'):
            return None

        random_name = uuid.uuid4().hex + '.csv'
        path = UPLOAD_DIRECTORY + '/' + random_name
        return path
