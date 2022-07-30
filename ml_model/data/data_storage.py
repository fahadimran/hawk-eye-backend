import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from utils.exceptions import DatabaseFileNotFound
from data.json_data_storage import JSONStorage


class FaceDataStore:

    def __init__(self, persistent_data_loc="data_file/facial_data.json") -> None:
        # persistent storage handler
        dir = os.getcwd()
        base_path, path = os.path.split(dir)
        persistent_data_loc = os.path.join(base_path, persistent_data_loc)
        self.db_handler = JSONStorage()
        saved_data = []


    def add_facial_data(self, facial_data):

        self.db_handler.add_data(face_data=facial_data)

    def remove_facial_data(self, face_id: str = None):

        self.db_handler.delete_data(face_id=face_id)

    def get_all_facial_data(self):

        return self.db_handler.get_all_data()
