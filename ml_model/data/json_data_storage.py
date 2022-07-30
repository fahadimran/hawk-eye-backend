import json
import os
import sys
from typing import Dict, List

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from utils.exceptions import DatabaseFileNotFound
from utils.validators import path_exists
from abstract_classes.storage import PersistentStorage


class JSONStorage(PersistentStorage):

    def __init__(self, db_loc: str = "ml_model/data_file/facial_data_db.json"):
        dir = os.getcwd()
        self.db_loc = os.path.join(dir, db_loc)

    def add_data(self, face_data: Dict):

        data = []
        # check if the db exists, otherwise create one
        base_path, filename = os.path.split(self.db_loc)

        if not path_exists(base_path):
            os.makedirs(base_path)
        if os.path.exists(self.db_loc):
            data = self.get_all_data()
        try:

            data.append(face_data)
            self.save_data(data=data)
        except Exception as exc:
            raise exc

    def get_all_data(self) -> List:

        if not path_exists(self.db_loc):
            raise DatabaseFileNotFound
        try:

            with open(self.db_loc, "r") as f:
                data = json.load(f)
                return self.sanitize_data(data)
        except Exception as exc:
            raise exc

    def delete_data(self, face_id: str) -> bool:

        all_data = self.get_all_data()
        num_entries = len(all_data)
        for idx, face_data in enumerate(all_data):
            for key_pair in face_data.items():
                # Check if the face id exists in current data item
                if face_id in key_pair:
                    all_data.pop(idx)

        if num_entries != len(all_data):
            self.save_data(data=all_data)

            return True
        return False

    def save_data(self, data: Dict = None):

        if data is not None:
            with open(self.db_loc, "w") as f:
                json.dump(data, f)

    def sanitize_data(self, data: List[Dict]) -> List[Dict]:

        for face_data in data:
            face_data["encoding"] = tuple(face_data["encoding"])
        return data



