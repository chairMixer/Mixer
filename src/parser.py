import os
import json
from enum import Enum

CHAIR_TYPE_NAMES = ["chair_back", "chair_seat", "chair_base", "chair_arm"]

class PartType(Enum):
    """
    https://github.com/FENGGENYU/PartNet_symh#d-the-labels-folder
    (0 -- back, 1 -- seat, 2 -- leg, and 3 -- armrest)
    """
    SEAT_BACK = 0
    SEAT_BASE = 1
    SEAT_LEG = 2
    SEAT_ARM = 3

    @staticmethod
    def get_name(_type):
        return CHAIR_TYPE_NAMES[_type]

class Part:
    def __init__(self, obs_file, name, _id, text):
        self.obs_file = obs_file
        self.name = name
        self._id = _id
        self.text = text
        pass

    def build_obb(self):
        """
        build the obb for this part
        """
        pass

    def in_obb(self, v):
        """
        is v in obb
        """
        pass
    
    def render(self, save=None, obb=False):
        """ 
        render the current obj
        """
        pass

    def __str__(self):
        return "Part({},{},{},{})".format(self.obs_file, self.name, self._id, self.text)


class Parts:
    def __init__(self, data_dir, type_id):
        self.parts = []
        self.num = None
        self.type_id = type_id
        self.data_dir = data_dir
        self.__load_data(data_dir, type_id)

    def __load_data(self, data_dir, type_id):
        with open(os.path.join(data_dir, 'result.json')) as f:
            structure = json.load(f)
        root = structure[0]
        for child in root['children']:
            if child['name'] == PartType.get_name(type_id):
                self.parts = self.get_parts(child, data_dir)
                self.num = len(self.parts)
                break

    @staticmethod
    def get_parts(root, data_dir):
        parts = []
        def find_parts(root):
            if 'objs' in root:
                part = Part(os.path.join(data_dir, root['objs'][0]),  # FIXME: can there be multiple obs for single part?
                    root['name'], root['id'], root['text'])
                parts.append(part)
                return
            else:
                if 'children' in root:
                    for child in root['children']:
                        find_parts(child)
        find_parts(root)
        return parts

    def __str__(self):
        return '{}:[{}]'.format(PartType.get_name(self.type_id), 
            ','.join([str(part) for part in self.parts]))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='test parser')
    parser.add_argument('data_dir', type=str,                         
                        help='data dir, like partnet/1173')
    parser.add_argument('type', type=int, choices=range(0, len(CHAIR_TYPE_NAMES)),                         
                        help='chair types, (0 -- back, 1 -- seat, 2 -- leg, and 3 -- armrest)')

    args = parser.parse_args()
    
    parts = Parts(args.data_dir, args.type)

    print(parts)