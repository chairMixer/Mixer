import numpy as np
import open3d as o3d
from pyobb.obb import OBB

def get_box_lines_set(box, color=[1, 0, 0]):
    points = box.points
    lines = [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 0],
        [4, 5],
        [5, 6],
        [6, 7],
        [7, 4],
        [1, 4],
        [2, 7],
        [3, 6],
        [0, 5],
    ]
    
    colors = [color for i in range(len(lines))]
    line_set = o3d.geometry.LineSet(
        points=o3d.utility.Vector3dVector(points),
        lines=o3d.utility.Vector2iVector(lines),
    )
    line_set.colors = o3d.utility.Vector3dVector(colors)

    return line_set

def render(obj_files, boxes=[]):
    render_sets = []

    for obj_file in obj_files:
        mesh = o3d.io.read_triangle_mesh(obj_file)
        mesh.compute_vertex_normals()
        render_sets.append(mesh)

    for box in boxes:
        box_line_set = get_box_lines_set(box)
        render_sets.append(box_line_set)
    o3d.visualization.draw_geometries(render_sets)

if __name__ == "__main__":
    from parser import Part, Parts, CHAIR_TYPE_NAMES
    import argparse
    parser = argparse.ArgumentParser(description='test parser')
    parser.add_argument('data_dir', type=str,                         
                        help='data dir, like partnet/1173')
    parser.add_argument('type', type=int, choices=range(0, len(CHAIR_TYPE_NAMES)),                         
                        help='chair types, (0 -- back, 1 -- seat, 2 -- leg, and 3 -- armrest)')

    args = parser.parse_args()
    
    parts = Parts(args.data_dir, args.type)
    render(map(lambda x: x.obj_file, parts), boxes=map(lambda x:x.obb, parts))

    # for part in parts:
    #     import pdb; pdb.set_trace()
    #     indices = np.reshape(part.f, (1,-1))[0]-1
    #     box = OBB.build_from_points(part.v[indices])
    #     print(part.obj_file)
    #     render([part.obj_file], boxes=[box])