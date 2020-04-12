# -*- coding: utf-8 -*-

import argparse
import random
import time
import scipy.misc as misc
import matplotlib.pyplot as plt
from matplotlib.pyplot import imread, imsave, imshow
import json
import os
import sys
import numpy as np
from subprocess import call
from collections import deque

import pathlib
current_dir = pathlib.Path(__file__).parent.absolute()

def load_obj(fn):
    fin = open(fn, 'r')
    lines = [line.rstrip() for line in fin]
    fin.close()

    vertices = []; faces = [];
    for line in lines:
        if line.startswith('v '):
            vertices.append(np.float32(line.split()[1:4]))
        elif line.startswith('f '):
            faces.append(np.int32([item.split('/')[0] for item in line.split()[1:4]]))

    f = np.vstack(faces)
    v = np.vstack(vertices)

    return v, f

def export_obj(out, v, f, color):
    mtl_out = out.replace('.obj', '.mtl')

    with open(out, 'w') as fout:
        fout.write('mtllib %s\n' % mtl_out)
        fout.write('usemtl m1\n')
        for i in range(v.shape[0]):
            fout.write('v %f %f %f\n' % (v[i, 0], v[i, 1], v[i, 2]))
        for i in range(f.shape[0]):
            fout.write('f %d %d %d\n' % (f[i, 0], f[i, 1], f[i, 2]))

    with open(mtl_out, 'w') as fout:
        fout.write('newmtl m1\n')
        fout.write('Kd %f %f %f\n' % (color[0], color[1], color[2]))
        fout.write('Ka 0 0 0\n')

    return mtl_out

def render_mesh(v, f, color=[0.216, 0.494, 0.722], show=True):
    tmp_dir = os.path.join(current_dir, 'tmp')
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    
    tmp_obj = os.path.join(tmp_dir, str(time.time()).replace('.', '_')+'_'+str(random.random()).replace('.', '_')+'.obj')
    tmp_png = tmp_obj.replace('.obj', '.png')

    tmp_mtl = export_obj(tmp_obj, v, f, color=color)

    # cmd = 'bash renderer/render.sh renderer/model.blend %s %s' % (tmp_obj, tmp_png)
    cmd = "{blender} {model} --background --python {python_script} -- {obj} {png}".format(
            blender="/Applications/Blender.app/Contents/MacOS/Blender",
            model=os.path.join(current_dir, "renderer", "model.blend"),
            python_script=os.path.join(current_dir, "renderer", "renderBatch.py"),
            obj=tmp_obj,
            png=tmp_png)

    call(cmd, shell=True)

    img = imread(tmp_png)

    cmd = 'rm -rf %s %s %s' % (tmp_obj, tmp_png, tmp_mtl)
    call(cmd, shell=True)

    if show:
        imshow(img)
        plt.show()

    return img

def render_parts(obj_files, save=False):
    root_v_list = []; root_f_list = []; tot_v_num = 0;
    for obj_file in obj_files:
        v, f = load_obj(obj_file)
        mesh = dict()
        mesh['v'] = v; mesh['f'] = f
        root_v_list.append(v)
        root_f_list.append(f+tot_v_num)
        tot_v_num += v.shape[0]

    root_v = np.vstack(root_v_list)
    root_f = np.vstack(root_f_list)

    center = np.mean(root_v, axis=0)
    root_v -= center
    scale = np.sqrt(np.max(np.sum(root_v**2, axis=1))) * 1.5
    root_v /= scale

    root_render = render_mesh(root_v, root_f, color=[0.93, 0.0, 0.0])

    alpha_part = root_render
    imshow(alpha_part)
    plt.show()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='test parts render')
    parser.add_argument('--files', type=str, action='append')

    args = parser.parse_args()
    
    render_parts(args.files)