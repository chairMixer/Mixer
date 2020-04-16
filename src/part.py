import os
import json
from enum import Enum
import util
from pyobb.obb import OBB
import numpy as np
import renderOpen3d
import open3d as o3d


CHAIR_TYPE_NAMES = ["chair_back", "chair_seat", "chair_base", "chair_arm", "chair"]


class PartType(Enum):
    """
    https://github.com/FENGGENYU/PartNet_symh#d-the-labels-folder
    (0 -- back, 1 -- seat, 2 -- leg, and 3 -- armrest)
    """
    SEAT_BACK = 0
    SEAT_BASE = 1
    SEAT_LEG = 2
    SEAT_ARM = 3
    CHAIR = 4

    @staticmethod
    def get_name(_type):
        return CHAIR_TYPE_NAMES[_type]

class Part:
    def __init__(self, obj_file, name, _id, text):
        self.obj_file = obj_file
        self.name = name
        self._id = _id
        self.text = text
        if obj_file != None:
            self.v, self.f = util.load_obj(obj_file)

    def render(self):
        _obb = self.obb
        renderOpen3d.render_with_vf([self.v], [self.f], [_obb])

    @property
    def obb(self):
        pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(self.v[np.reshape(self.f, (1,-1))[0]-1]))
        _obb = pcd.get_axis_aligned_bounding_box()
        return _obb

    def __str__(self):
        return "Part({},{},{},{})".format(self.obj_file, self.name, self._id, self.text)

    def affine_trans(self, matrix):
        """
        apply affine transformation
        matrix: 4 by 4 ndarray
        """
        new_v = []
        for v in self.v:
            # import pdb; pdb.set_trace()
            a = np.ones((4,1))
            a[0:3,0] = v[:]
            b = np.dot(matrix, a)
            new_v.append(b[:3,0])
        self.v = np.asarray(new_v)


class Parts:
    def __init__(self, data_dir, type_id):
        self._parts = []
        self.num = None
        self.type_id = type_id
        self.data_dir = data_dir
        if data_dir != None:
            self.__load_data(data_dir, type_id)

    def __load_data(self, data_dir, type_id):
        with open(os.path.join(data_dir, 'result.json')) as f:
            structure = json.load(f)
        root = structure[0]
        for child in root['children']:
            if child['name'] == PartType.get_name(type_id):
                self._parts = Parts.get_parts(child, data_dir)
                self.num = len(self._parts)
                break
    
    @staticmethod
    def get_parts(root, data_dir):
        parts = []
        def find_parts(root):
            if 'objs' in root:
                part = Part(os.path.join(data_dir, "objs", root['objs'][0]+'.obj'),  # FIXME: can there be multiple objs for single part?
                    root['name'], root['id'], root['text'])
                parts.append(part)
                return
            else:
                if 'children' in root:
                    for child in root['children']:
                        find_parts(child)
        find_parts(root)
        return parts

    def render(self, idv_boxes=False):
        renderOpen3d.render_with_vf(list(map(lambda x: x.v, self._parts)), 
            list(map(lambda x: x.f, self._parts)), list(map(lambda x: x.obb, self._parts)))

    def translate(self, v):
        for part in self._parts:
            mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(part.v),o3d.utility.Vector3iVector(part.f-1))
            mesh = mesh.translate(np.asarray(v))
            part.v = np.asarray(mesh.vertices)
    
    def scale(self, v):
        for part in self._parts:
            mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(part.v),o3d.utility.Vector3iVector(part.f-1))
            mesh = mesh.scale(np.asarray(v))
            part.v = np.asarray(mesh.vertices)
    
    def merge(self):
        if self._parts:
            result = Part(None, "merged", self.type_id, "Merged") #TODO: name properly
            result.v = np.array([], dtype=np.float32).reshape(0,3)
            result.f = np.array([], dtype=np.int32).reshape(0,3)
            offset = 0
            for part in self._parts:
                result.v = np.vstack([result.v, part.v])
                result.f = np.vstack([result.f, part.f + offset])
                offset += part.v.shape[0]
            self._parts = [result]

    def __str__(self):
        return '{}:[{}]'.format(PartType.get_name(self.type_id), 
            ','.join([str(part) for part in self._parts]))

    def __iter__(self):
        return iter(self._parts)


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
    import pdb; pdb.set_trace()

    # # Test transition
    # parts._parts[0].affine_trans(np.asarray([[1,0,0,0],[0,1,0,10], [0,0,1,0], [0,0,0,1]]))
    
    parts.render()

    # for part in parts:
    #     part.render()