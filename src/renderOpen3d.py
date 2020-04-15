import numpy as np
import open3d as o3d
from pyobb.obb import OBB
import sklearn.decomposition


def get_normal_lines_set(normals, color=[0, 1, 0]):
    points = np.vstack([[[0,0,0]], normals*2])
    lines = [
        [0, 1],
        [0, 2],
        [0, 3],
    ]
    
    colors = [color for i in range(len(lines))]
    line_set = o3d.geometry.LineSet(
        points=o3d.utility.Vector3dVector(points),
        lines=o3d.utility.Vector2iVector(lines),
    )
    line_set.colors = o3d.utility.Vector3dVector(colors)

    return line_set


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


def render_with_vf(vs, fs, boxes, pca_on=False, pcd_on=False):
    render_sets = [o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=0.6, origin=[0, 0, 0])] 
    for i, _ in enumerate(vs):
        v,f, box = vs[i], fs[i], boxes[i]
        mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(v),o3d.utility.Vector3iVector(f-1))
        render_sets.append(mesh)
        render_sets.append(box)

        if pcd_on:
            pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(v[np.reshape(f, (1,-1))[0]-1]))
            render_sets.append(pcd)

        if pca_on:
            pca = sklearn.decomposition.PCA(3)
            pca.fit(v)
            print("pca components", pca.components_)
            print("pca variance ratio", pca.explained_variance_ratio_)
            print("pca variance", pca.explained_variance_)

            render_sets.append(mesh)

            normal_lines_set = get_normal_lines_set(pca.components_)
            render_sets.append(normal_lines_set)
        

    o3d.visualization.draw_geometries(render_sets)


def render_with_files(obj_files):

    render_sets = [o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=0.6, origin=[0, 0, 0])] 

    for obj_file in obj_files:
        mesh = o3d.io.read_triangle_mesh(obj_file)
        mesh.compute_vertex_normals()
        render_sets.append(mesh)

        box = OBB.build_from_points(np.asarray(mesh.vertices)[np.reshape(np.asarray(mesh.triangles), (1,-1))[0]])
        box_line_set = get_box_lines_set(box)
        render_sets.append(box_line_set)

    o3d.visualization.draw_geometries(render_sets)


if __name__ == "__main__":
    from part import Part, Parts, CHAIR_TYPE_NAMES
    import argparse
    parser = argparse.ArgumentParser(description='test parser')
    parser.add_argument('data_dir', type=str,                         
                        help='data dir, like partnet/1173')
    parser.add_argument('type', type=int, choices=range(0, len(CHAIR_TYPE_NAMES)),                         
                        help='chair types, (0 -- back, 1 -- seat, 2 -- leg, and 3 -- armrest)')

    args = parser.parse_args()
    
    parts = Parts(args.data_dir, args.type)
    # render_with_files(map(lambda x: x.obj_file, parts))

    render_with_vf(list(map(lambda x: x.v, parts)), 
        list(map(lambda x: x.f, parts)), list(map(lambda x: x.obb, parts)), pca_on=True, pcd_on=True)

    # for part in parts:
    #     import pdb; pdb.set_trace()
    #     indices = np.reshape(part.f, (1,-1))[0]-1
    #     box = OBB.build_from_points(part.v[indices])
    #     print(part.obj_file)
    #     render([part.obj_file], boxes=[box])