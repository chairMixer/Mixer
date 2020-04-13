from pytest import mark
from math import pi, cos, sin, sqrt, radians
from pyobb.obb import OBB
import numpy as np
import parser
from parser import Part, Parts, CHAIR_TYPE_NAMES

EPSILON = 0.025


def tpl_cmp(a, b, epsilon=EPSILON):
    for aX, bX in zip(a, b):
        if abs(aX - bX) > epsilon:
            return False
    return True


def render_to_png(filename, callback, obb, model_matrix=(1, 0, 0, 0,
                                                         0, 1, 0, 0,
                                                         0, 0, 1, 0,
                                                         0, 0, 0, 1)):
    from pygame import init, display, quit
    from pygame.constants import OPENGL, DOUBLEBUF
    from OpenGL.GL import glLightfv, glCullFace, glEnable, glShadeModel, glMatrixMode, glLoadIdentity, glClear, \
        glLoadMatrixf, glPolygonMode, glCallList, glReadPixels, GL_LIGHT0, GL_POSITION, GL_AMBIENT, GL_DIFFUSE, \
        GL_BACK, GL_LIGHTING, GL_COLOR_MATERIAL, GL_DEPTH_TEST, GL_SMOOTH, GL_PROJECTION, GL_MODELVIEW, \
        GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_FRONT_AND_BACK, GL_FILL, GL_LINE, GL_BGR, GL_UNSIGNED_BYTE
    from OpenGL.GLU import gluPerspective
    from cv2 import imwrite
    from numpy import frombuffer, uint8
    init()
    viewport = (800, 600)
    display.set_mode(viewport, OPENGL | DOUBLEBUF)
    glLightfv(GL_LIGHT0, GL_POSITION, (0, -1, 0, 0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1))
    glCullFace(GL_BACK)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    width, height = viewport
    gluPerspective(90.0, width / float(height), 0.1, 100.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glLoadMatrixf(model_matrix)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glCallList(callback())
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glCallList(create_obb_gl_list(obb))
    img_data = glReadPixels(0, 0, width, height, GL_BGR, GL_UNSIGNED_BYTE)
    img = frombuffer(img_data, dtype=uint8)
    img = img.reshape((height, width, 3))
    imwrite(filename, img)
    quit()


def create_obb_gl_list(obb):
    from OpenGL.GL import glGenLists, glNewList, glFrontFace, glBegin, glEnd, glEndList, glColor3fv, glVertex3fv, \
        GL_CCW, GL_COMPILE, GL_LINES
    gl_list = glGenLists(1)
    glNewList(gl_list, GL_COMPILE)
    glFrontFace(GL_CCW)
    glBegin(GL_LINES)
    glColor3fv((1, 0, 0))

    def input_vertex(x, y, z):
        glVertex3fv((obb.rotation[0][0] * x + obb.rotation[0][1] * y + obb.rotation[0][2] * z,
                     obb.rotation[1][0] * x + obb.rotation[1][1] * y + obb.rotation[1][2] * z,
                     obb.rotation[2][0] * x + obb.rotation[2][1] * y + obb.rotation[2][2] * z))

    input_vertex(*obb.max)
    input_vertex(obb.max[0], obb.min[1], obb.max[2])

    input_vertex(obb.max[0], obb.min[1], obb.max[2])
    input_vertex(obb.min[0], obb.min[1], obb.max[2])

    input_vertex(obb.min[0], obb.min[1], obb.max[2])
    input_vertex(obb.min[0], obb.max[1], obb.max[2])

    input_vertex(obb.min[0], obb.max[1], obb.max[2])
    input_vertex(*obb.max)

    input_vertex(obb.max[0], obb.max[1], obb.max[2])
    input_vertex(obb.max[0], obb.max[1], obb.min[2])

    input_vertex(obb.max[0], obb.min[1], obb.max[2])
    input_vertex(obb.max[0], obb.min[1], obb.min[2])

    input_vertex(obb.min[0], obb.max[1], obb.max[2])
    input_vertex(obb.min[0], obb.max[1], obb.min[2])

    input_vertex(obb.min[0], obb.min[1], obb.max[2])
    input_vertex(obb.min[0], obb.min[1], obb.min[2])

    input_vertex(obb.max[0], obb.max[1], obb.min[2])
    input_vertex(obb.max[0], obb.min[1], obb.min[2])

    input_vertex(obb.max[0], obb.min[1], obb.min[2])
    input_vertex(*obb.min)

    input_vertex(*obb.min)
    input_vertex(obb.min[0], obb.max[1], obb.min[2])

    input_vertex(obb.min[0], obb.max[1], obb.min[2])
    input_vertex(obb.max[0], obb.max[1], obb.min[2])

    glEnd()
    glEndList()

    return gl_list


def create_gl_list(shape):
    from OpenGL.GL import glGenLists, glNewList, glFrontFace, glBegin, glEnd, glEndList, glNormal3fv, glVertex3fv, \
        GL_COMPILE, GL_CCW, GL_TRIANGLES
    vertices = shape['vertices']
    normals = shape['normals']
    indices = shape['indices']
    gl_list = glGenLists(1)
    glNewList(gl_list, GL_COMPILE)
    glFrontFace(GL_CCW)
    glBegin(GL_TRIANGLES)
    for idx in indices:
        glNormal3fv(normals[idx])
        glVertex3fv(vertices[idx])
    glEnd()
    glEndList()
    return gl_list


def sphere(radius, center, num_slices):
    theta_step = 2.0 * pi / (num_slices - 1)
    phi_step = pi / (num_slices - 1.0)
    theta = 0.0
    vertices = []
    normals = []
    for i in range(0, num_slices):
        cos_theta = cos(theta)
        sin_theta = sin(theta)
        phi = 0.0
        for j in range(0, num_slices):
            x = -sin(phi) * cos_theta
            y = -cos(phi)
            z = -sin(phi) * sin_theta
            n = sqrt(x * x + y * y + z * z)
            if n < 0.99 or n > 1.01:
                x /= n
                y /= n
                z /= n
            normals.append((x, y, z))
            vertices.append((x * radius + center[0],
                             y * radius + center[1],
                             z * radius + center[2]))
            phi += phi_step
        theta += theta_step
    indices = []
    for i in range(0, num_slices - 1):
        for j in range(0, num_slices - 1):
            base_idx = (i * num_slices + j)
            indices.append(base_idx)
            indices.append(base_idx + num_slices)
            indices.append(base_idx + num_slices + 1)
            indices.append(base_idx)
            indices.append(base_idx + num_slices + 1)
            indices.append(base_idx + 1)

    return {'vertices': vertices,
            'normals': normals,
            'indices': indices}


def prepare_mesh(v, f):
    vertices = []
    normals = []

    def new_vertex(x, y, z):
        vertices.append((x, y, z))
        normals.append((x, y, z))

    for vertex in v:
        new_vertex(vertex[0], vertex[1], vertex[2])

    for i in range(0, len(normals), 3):
        v0 = normals[i]
        v1 = normals[i + 1]
        v2 = normals[i + 2]
        a = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
        b = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
        cross = (a[1] * b[2] - a[2] * b[1],
                 a[2] * b[0] - a[0] * b[2],
                 a[0] * b[1] - a[1] * b[0])
        length = sqrt(cross[0] * cross[0] + cross[1] * cross[1] + cross[2] * cross[2])
        if length > 0:
            normal = (cross[0] / length, cross[1] / length, cross[2] / length)
        else:
            # degenerate normal
            normal = (0, 0, 0)
        normals[i] = normal
        normals[i + 1] = normal
        normals[i + 2] = normal

    return {'vertices': vertices,
            'normals': normals,
            'indices': f-1}



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='test parser')
    parser.add_argument('data_dir', type=str,                         
                        help='data dir, like partnet/1173')
    parser.add_argument('type', type=int, choices=range(0, len(CHAIR_TYPE_NAMES)),                         
                        help='chair types, (0 -- back, 1 -- seat, 2 -- leg, and 3 -- armrest)')

    args = parser.parse_args()
    
    parts = Parts(args.data_dir, args.type)
    import pdb; pdb.set_trace()
    for part in parts:
        obb = OBB.build_from_triangles(part.v, np.reshape(part.f, (1,-1))[0]-1)
        mesh = prepare_mesh(part.v, np.reshape(part.f, (1,-1))[0]-1)
        render_to_png('test_obb_size.png', lambda: create_gl_list(mesh), obb, (1,  0,  0,  0,
                                                                             0,  1,  0,  0,
                                                                             0,  0,  1,  0,
                                                                             0,  0, -5,  1))
