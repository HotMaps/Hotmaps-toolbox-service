import uuid
from ..constants import UPLOAD_DIRECTORY


class FileSystem:
    """
    A class containing helper operations related to File System
    """
    @staticmethod
    def save_file_csv_random_name(content: str):
        """
        Save a file into a temp folder with a random name
        :param content: the content of the file you want to write
        :return random_name: the name randomly generated
        """
        random_name = uuid.uuid4().hex
        path = UPLOAD_DIRECTORY + '/' + content + '.csv'
        f = open(path, 'w')
        f.write(content)
        f.close()
        return random_name
