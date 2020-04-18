import os
import open3d as o3d


def render(obj_file):
    mesh = o3d.io.read_triangle_mesh(obj_file)
    o3d.visualization.draw_geometries([mesh])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='color obj viewer')
    parser.add_argument('obj', type=str,                         
                        help='obj file path')

    args = parser.parse_args()
    render(args.obj)
    



