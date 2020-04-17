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
from PIL import Image

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

def render_mesh(v, f, color=[0.216, 0.494, 0.722]):
    tmp_dir = os.path.join(current_dir, 'tmp')
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    tmp_obj = os.path.join(tmp_dir, str(time.time()).replace('.', '_')+'_'+str(random.random()).replace('.', '_')+'.obj')
    tmp_png_top = tmp_obj.replace('.obj', '_top')
    tmp_png_top = tmp_png_top + '.png'
    tmp_png_front = tmp_png_top.replace('_top', '_front')
    tmp_png_left = tmp_png_top.replace('_top', '_left')

    tmp_mtl = export_obj(tmp_obj, v, f, color=color)

    # cmd = 'bash renderer/render.sh renderer/model.blend %s %s' % (tmp_obj, tmp_png)
    cmd = "{blender} {model} --background --python {python_script} -- {obj} {png_top} {png_front} {png_left}".format(
            blender="/Applications/Blender.app/Contents/MacOS/Blender",
            model=os.path.join(current_dir, "renderer", "model.blend"),
            python_script=os.path.join(current_dir, "renderer", "renderBatch.py"),
            obj=tmp_obj,
            png_top=tmp_png_top,
            png_front = tmp_png_front,
            png_left = tmp_png_left)

    call(cmd, shell=True)

    # img_top = imread(tmp_png_top)
    # img_front = imread(tmp_png_front)
    # img_left = imread(tmp_png_left)

    img_top = Image.open(tmp_png_top).convert('L')
    img_front = Image.open(tmp_png_front).convert('L')
    img_left = Image.open(tmp_png_left).convert('L')

    cmd = 'rm -rf %s %s %s %s %s' % (tmp_obj, tmp_png_top, tmp_png_front, tmp_png_left, tmp_mtl)
    call(cmd, shell=True)

    return img_top, img_front, img_left

def render_parts(obj_folder, save=False):
    dir = os.path.join(current_dir, 'orthographic_view')
    if not os.path.exists(dir):
        os.mkdir(dir)
    count = 1

    # for obj_file in obj_files:
    for obj_file in sorted(os.listdir(args.folder)):
        obj_v_list = []; obj_f_list = []; obj_v_num = 0;
        v, f = load_obj(os.path.join(obj_folder, obj_file))
        mesh = dict()
        mesh['v'] = v; mesh['f'] = f
        obj_v_list.append(v)
        obj_f_list.append(f+obj_v_num)
        obj_v_num += v.shape[0]

        obj_v = np.vstack(obj_v_list)
        obj_f = np.vstack(obj_f_list)

        center = np.mean(obj_v, axis=0)
        obj_v -= center
        scale = np.sqrt(np.max(np.sum(obj_v**2, axis=1))) * 1.5
        obj_v /= scale

        obj_top, obj_front, obj_left = render_mesh(obj_v, obj_f, color=[0, 0, 0])
        
        save_path1 = "{str_count}.bmp".format(str_count=count)
        save_path1 = os.path.join(dir, save_path1)
        save_path2 = "{str_count}.bmp".format(str_count=count+1)
        save_path2 = os.path.join(dir, save_path2)
        save_path3 = "{str_count}.bmp".format(str_count=count+2)
        save_path3 = os.path.join(dir, save_path3)

        obj_front.save(save_path1)
        obj_left.save(save_path2)
        obj_top.save(save_path3)

        count += 3

        # plt.figure()
        # imshow(obj_top)
        # plt.figure()
        # imshow(obj_front)
        # plt.figure()
        # imshow(obj_left)
        # plt.show()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='test parts render')
    # parser.add_argument('--files', type=str, action='append')
    parser.add_argument('--folder', type=str)

    args = parser.parse_args()

    # render_parts(args.files)

    render_parts(args.folder)
