import os
import json
from enum import Enum
import util
from pyobb.obb import OBB
import numpy as np
import renderOpen3d
import open3d as o3d
import bb


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
    def __init__(self, obj_file, name, _id, text):
        self.obj_file = obj_file
        self.name = name
        self._id = _id
        self.text = text
        self.v, self.f = util.load_obj(obj_file)

    def render(self):
        _obb = self.obb
        renderOpen3d.render_with_vf([self.v], [self.f], [_obb])

    def get_points(self):
        return self.v[np.reshape(self.f, (1,-1))[0]-1]

    @property
    def obb(self):
        pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(self.v[np.reshape(self.f, (1,-1))[0]-1]))
        _obb = pcd.get_oriented_bounding_box()
        return _obb

    def scale(self, s):
        mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(self.v),o3d.utility.Vector3iVector(self.f-1))
        mesh = mesh.scale(s)
        self.v = np.asarray(mesh.vertices)

    def __str__(self):
        return "Part({},{},{},{})".format(self.obj_file, self.name, self._id, self.text)

    def affine_trans(self, matrix):
        """
        apply affine transformation
        matrix: 4 by 4 ndarray
        """
        new_v = []
        for v in self.v:
            a = np.ones((4,1))
            a[0:3,0] = v[:]
            b = np.dot(matrix, a)
            new_v.append(b[:3,0])
        self.v = np.asarray(new_v)

    def output(self, out_file, color=np.asarray([0.5,0.5,0.5])):
        mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(self.v),o3d.utility.Vector3iVector(self.f-1))
        mesh.paint_uniform_color(color)
        o3d.io.write_triangle_mesh(out_file, mesh, write_vertex_normals=False)

class Parts:
    def __init__(self, data_dir, type_id):
        self._parts = []
        self.num = None
        self.type_id = type_id
        self.data_dir = data_dir
        self.__load_data(data_dir, type_id)

    def __load_data(self, data_dir, type_id):
        if data_dir is None:
            return
        with open(os.path.join(data_dir, 'result.json')) as f:
            structure = json.load(f)
        root = structure[0]
        for child in root['children']:
            if child['name'] == PartType.get_name(type_id):
                self._parts = Parts.get_parts(child, data_dir)
                self.num = len(self._parts)
                break

    @property
    def yaabb(self):
        """
        y-axis aligned bounding box
        """
        if len(self._parts) == 0:
            return None
        v = np.vstack([part.v[[np.reshape(part.f, (1,-1))[0]-1]] for part in self._parts])
        _yaabb = bb.YAABB(v)
        return _yaabb
    
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

    def get_render_sets(self):
        if len(self._parts) > 0:
            return renderOpen3d.get_render_sets(list(map(lambda x: x.v, self._parts)), 
                list(map(lambda x: x.f, self._parts)), list(map(lambda x: x.obb, self._parts)), bb_points=self.yaabb.corners)
        else:
            return []

    def render(self, idv_boxes=False):
        if len(self._parts) > 0:
            renderOpen3d.render_with_vf(list(map(lambda x: x.v, self._parts)), 
                list(map(lambda x: x.f, self._parts)), list(map(lambda x: x.obb, self._parts)), bb_points=self.yaabb.corners)

    def translation(self, d):
        """
        d is a 1*3 vector
        """
        matrix = np.eye(4)
        matrix[:3, 3] = d[:]
        self.affine_trans(matrix)

    def scale(self, s):
        for _part in self._parts:
            _part.scale(s)

    def affine_trans(self, matrix):
        for _part in self._parts:
            _part.affine_trans(matrix)

    def __str__(self):
        return '{}:[{}]'.format(PartType.get_name(self.type_id), 
            ','.join([str(part) for part in self._parts]))

    def __iter__(self):
        return iter(self._parts)

    def output(self, out_file=None, color=np.asarray([0.5,0.5,0.5])):
        vs = []
        fs = []
        offset = 0
        if len(self._parts) == 0:
            return None, None
        for _part in self._parts:
            vs.append(_part.v)
            fs.append(_part.f+offset)
            offset += _part.v.shape[0]
        v = np.vstack(vs)
        f = np.vstack(fs)
        if out_file is not None:
            mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(v),o3d.utility.Vector3iVector(f-1))
            mesh.paint_uniform_color(color)
            o3d.io.write_triangle_mesh(out_file, mesh, write_vertex_normals=False)
        return v, f


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

    # # Test transition
    # parts._parts[0].affine_trans(np.asarray([[1,0,0,0],[0,1,0,10], [0,0,1,0], [0,0,0,1]]))
    
    # parts.render()
    
    # parts._parts[0].output("tmp.obj", color=[1.0, 0, 0])
    # mesh = o3d.io.read_triangle_mesh("tmp.obj")
    # o3d.visualization.draw_geometries([mesh])

    parts.output(out_file="tmp.obj", color=[1.0, 0, 0])
    mesh = o3d.io.read_triangle_mesh("tmp.obj")
    o3d.visualization.draw_geometries([mesh])

    print(parts.yaabb)

    # for part in parts:
    #     part.render()