import os
import requests
import uuid
import xml.etree.ElementTree as ET
import shutil
from app import celery
from app.model import run_command, commands_in_array
from .. import constants, dbGIS as db
from ..decorators.exceptions import RequestException
from .. import secrets
ALLOWED_EXTENSIONS = set(['tif', 'csv'])


class Uploads(db.Model):
    '''
    This class will describe the model of a file uploaded by a user
    '''
    __tablename__ = 'uploads'
    __table_args__ = (
        {"schema": 'user'}
    )

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255))
    name = db.Column(db.String(255))
    layer = db.Column(db.String(255))
    size = db.Column(db.Numeric)
    url = db.Column(db.String(255))
    is_generated = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.users.id'))


class ColorMap:
    '''
    This class is used to access all informations necessary to upload a .tif to the server separating it into tiles
    '''
    def __init__(self, r, g, b, a, quantity):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.quantity = quantity


@celery.task(name = 'generate_tiles_file_upload')
def generate_tiles(upload_folder, grey_tif, layer, upload_uuid, user_currently_used_space):
    '''
    This function is used to generate the various tiles of a layer in the db.
    :param upload_folder: the folder of the upload
    :param grey_tif: the url to the input file
    :param layer: the name of the layer choosen for the input
    :param upload_uuid: the uuid of the upload
    :param user_currently_used_space: the space currently used by the user

    '''
    # we set up the directory for the tif
    directory_for_tiles = upload_folder + '/tiles'

    tile_path = directory_for_tiles
    access_rights = 0o755
    try:
        os.mkdir(tile_path, access_rights)
    except OSError:
        print ("Creation of the directory %s failed" % tile_path)
    else:
        print ("Successfully created the directory %s" % tile_path)

    # get the sld file
    url = secrets.GEOSERVER_API_URL + 'styles/' + layer + '.sld'
    auth = secrets.GEOSERVER_AUTH
    result = requests.get(url, auth=auth)
    xml = result.content
    color_map_objects = extract_colormap(xml)

    # we want to use a unique id for the file to be sure that it will not be duplicated in case two
    uuid_temp = str(uuid.uuid4())
    grey2rgb_path = create_grey2rgb_txt(color_map_objects, uuid_temp)
    rgb_tif = upload_folder + '/rgba.tif'

    try:
        # commands launch to obtain the level of zooms
        args_rgba = commands_in_array("gdaldem color-relief {} {} -alpha {}".format(grey_tif, grey2rgb_path, rgb_tif))
        run_command(args_rgba)
        #os.system(com_create_rgba)

        # commands launch to obtain the level of zooms
        args_tiles = commands_in_array("python app/helper/gdal2tiles.py -p 'mercator' -w 'leaflet' -r 'near' -z 4-11 {} {} ".format(rgb_tif, tile_path))
        run_command(args_tiles)
        #os.system(com_generate_tiles)
    except:
        generate_state = 10
    else:
        generate_state = 0

    # we delete all temp files
    for fname in os.listdir('/tmp'):
        if fname.startswith(uuid_temp):
            os.remove(os.path.join('/tmp', fname))

    # updating generate state of upload
    upload = Uploads.query.filter_by(uuid=upload_uuid).first()
    upload.is_generated = generate_state
    db.session.commit()

    check_map_size(upload_folder, user_currently_used_space, upload_uuid)
    return generate_state


def check_map_size(upload_folder, user_currently_used_space, upload_uuid):
    '''
    This method is used to check the size of the file
    :param upload_folder: the folder where the upload is stored
    :param user_currently_used_space: the space already used by the user
    :param upload_uuid: the uuid of the upload
    :return:
    '''
    size = 0
    for dirpath, dirnames, filenames in os.walk(upload_folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            size += float(os.path.getsize(fp)) / 1000000
    # we need to check if there is enough disk space for the dataset
    total_used_space = user_currently_used_space + size
    upload = Uploads.query.filter_by(uuid=upload_uuid).first()
    if total_used_space > constants.USER_DISC_SPACE_AVAILABLE:
        db.session.delete(upload)
        shutil.rmtree(upload_folder)
    else:
        upload.size = size
    db.session.commit()


def create_grey2rgb_txt(color_map_objects, uuid_upload):
    '''
    This method will create the grey2rgb.txt file in the /tmp folder in order to convert the .tif to the rgb format
    :param color_map_objects: the list of ColorMap required
    :param uuid_upload: the uuid in order to have a single file
    :return: the file path
    '''
    # create the path and the file
    grey2rgb_path = '/tmp/' + uuid_upload + 'grey2rgb.txt'
    grey2rgb = open(grey2rgb_path, 'w')

    # complete the file
    for color_map_object in color_map_objects:
        grey2rgb.write(
            str(color_map_object.quantity) + " " +
            str(color_map_object.r) + " " +
            str(color_map_object.g) + " " +
            str(color_map_object.b) + " " +
            str(color_map_object.a) + "\r\n"
        )

    # close the file connection and return the path
    grey2rgb.close()
    return grey2rgb_path


def extract_colormap(xml):
    '''
    This method will extract the colormap of a sld stylesheet
    :param xml: the xml file
    :return: an array of the different color map
    '''
    # create the xml tree
    try:
        root = ET.fromstring(xml)
    except Exception as e:
        raise RequestException(str(xml))
    ns = {'sld': 'http://www.opengis.net/sld'}
    # get the list of Color map
    color_map_list = root.findall(".//sld:ColorMapEntry", ns)
    color_map_objects = []
    # for each color map get the color, the opacity and the quantity
    for color_map in color_map_list:
        color_tuple = hex_to_rgb(color_map.get('color'))
        opacity = int(float(color_map.get('opacity')) * 255)
        quantity = color_map.get('quantity')
        color_map_object = ColorMap(color_tuple[0], color_tuple[1], color_tuple[2], opacity, quantity)

        # add the color map object to the list
        color_map_objects.append(color_map_object)
    return color_map_objects


def hex_to_rgb(value):
    '''
    This method is used to convert an hexadecimal into a tuple of rgb values
    :param value: hexadecimal
    :return: a tuple of rgb
    '''
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def calculate_total_space(uploads):
    '''
    This method will calculate the amount of disc space taken by a list of uploads
    :param uploads:
    :return: the used disk space
    '''
    used_size = float(0)

    # sum of every size
    for upload in uploads:
        used_size += float(upload.size)

    return used_size


def allowed_file(filename):
    '''
    This method will check if the file is allowed
    :param filename:
    :return:
    '''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

