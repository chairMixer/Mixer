import os
import random
import numpy as np
import chair
import open3d as o3d
import time
from datetime import datetime

import pathlib
current_dir = pathlib.Path(__file__).parent.absolute()

def output(out_dir, chair):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    now = datetime.now()
    timestamp = now.strftime('%Y%m%d%H%M%S')
    out_obj = os.path.join(out_dir, timestamp+'.obj')
    out_png = os.path.join(out_dir, timestamp+'.png')

    v, f, c = chair.output(out_obj)
    mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(v),o3d.utility.Vector3iVector(f-1))
    mesh.vertex_colors = o3d.utility.Vector3dVector(c)

    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(mesh)
    vis.update_geometry(mesh)
    ctr = vis.get_view_control()
    parameters = o3d.io.read_pinhole_camera_parameters(os.path.join(current_dir, "DepthCamera.json"))
    ctr.convert_from_pinhole_camera_parameters(parameters)
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image(out_png)
    vis.destroy_window()

def mixer(data_dir, out_dir, num):
    chair_ids = []
    for _, dirs, _ in os.walk(data_dir):
        chair_ids = dirs
        break
    count = 0
    while count < num:
        base_source = random.choice(chair_ids)
        back_source = random.choice(chair_ids)
        leg_source = random.choice(chair_ids)
        if len(set([base_source, back_source, leg_source])) >= 2:
            base_chair = chair.Chair(os.path.join(data_dir, base_source))
            back = chair.Chair(os.path.join(data_dir, back_source)).back
            leg =  chair.Chair(os.path.join(data_dir, leg_source)).leg

            if len(base_chair.arm._parts) > 0:
                new_chair = chair.Chair(None)
                new_chair.base = base_chair.base
                new_chair.arm = base_chair.arm
                new_chair.leg = leg
                new_chair.back = back
                output(out_dir, new_chair)
                count += 1

            new_chair = chair.Chair(None)
            new_chair.base = base_chair.base
            new_chair.leg = leg
            new_chair.back = back
            output(out_dir, new_chair)
            count += 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='test parser')
    parser.add_argument('input_dir', type=str,                         
                        help='input data dir, like partnet')
    parser.add_argument('output_dir', type=str,                         
                        help='output data dir')
    parser.add_argument('num', type=int,
                        help='number of new chairs to generate')

    args = parser.parse_args()

    mixer(args.input_dir, args.output_dir, args.num)

    # mixer("../../../final/a/", "../output/with_arm/a/")
    # mixer("../../../final/b/", "../output/with_arm/b/")
    # mixer("../../../final/c", "../output/with_arm/c/")

