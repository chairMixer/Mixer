import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import numpy as np
import open3d as o3d

class OBB2D:

    def __init__(self, points):
        """
        points: shape (n,2) np array
        """
        self.center, self.corners = OBB2D.get_2dobb(points)
        
    @staticmethod
    def get_2dobb(a):
        ca = np.cov(a, y = None,rowvar = 0,bias = 1)

        v, vect = np.linalg.eig(ca)
        tvect = np.transpose(vect)

        #use the inverse of the eigenvectors as a rotation matrix and
        #rotate the points so they align with the x and y axes
        ar = np.dot(a,np.linalg.inv(tvect))

        # get the minimum and maximum x and y 
        mina = np.min(ar,axis=0)
        maxa = np.max(ar,axis=0)
        diff = (maxa - mina)*0.5

        # the center is just half way between the min and max xy
        center = mina + diff

        #get the 4 corners by subtracting and adding half the bounding boxes height and width to the center
        corners = np.array([center+[-diff[0],-diff[1]],center+[diff[0],-diff[1]],center+[diff[0],diff[1]],center+[-diff[0],diff[1]]])

        #use the the eigenvectors as a rotation matrix and
        #rotate the corners and the centerback
        corners = np.dot(corners,tvect)
        center = np.dot(center,tvect)

        return center, corners


class YAABB:
    """
    Y axis aligned bounding box
    """
    def __init__(self, v):
        # v_xz = v[:,[0,2]] # project to xz plane
        # self.obb_xz = OBB2D(v_xz)
        p = np.copy(v)
        p[:,1] = 0
        for i in range(1,2):
            temp = np.copy(v)
            temp[:,1] = float(i)/10.0
            p = np.vstack([p, temp])
        _obb = o3d.geometry.OrientedBoundingBox.create_from_points(o3d.utility.Vector3dVector(p))
        self.corners = np.asarray(_obb.get_box_points())
        self.center = np.asarray(_obb.get_center())[[0,2]]

        self.y_min = np.min(v[:, 1], axis=0)
        self.y_max = np.max(v[:, 1], axis=0)
        lowers = np.where(self.corners[:,1] < 0.05)[0]
        uppers = np.where(self.corners[:,1] > 0.05)[0]
        self.corners[lowers, 1] = self.y_min
        self.corners[uppers, 1] = self.y_max

    def __str__(self):
        return "{}".format(self.corners)


if __name__ == "__main__":
    
    # a  = np.asarray([(3.7, 1.7), (4.1, 3.8), (4.7, 2.9), (5.2, 2.8), (6.0,4.0), (6.3, 3.6), (9.7, 6.3), (10.0, 4.9), (11.0, 3.6), (12.5, 6.4)])
    a  = np.asarray([(1.0,0), (0,1.0), (-1.0,0), (0.0,-1.0)])
    
    # fig = plt.figure(figsize=(12,12))
    # ax = fig.add_subplot(111)

    ax.scatter(a[:,0],a[:,1])
    obb2d = OBB2D(a)
    center, corners = obb2d.center, obb2d.corners
    ax.scatter([center[0]],[center[1]]) 
    corners = np.vstack([corners[:], corners[0]])
    ax.plot(corners[:,0],corners[:,1],'-')


    # FIXME: oreders are wrong
    levels = 4
    b = []
    for level in range(levels):
        b += [(e[0], level, e[1]) for e in a]
    b = np.asarray(b)
    yaabb = YAABB(b)
    print(yaabb.corners)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(b[:, 0], b[:, 2], b[:, 1])
    plot_corners = np.vstack([yaabb.corners[:4], yaabb.corners[0], yaabb.corners[4:], yaabb.corners[4]])
    ax.plot(plot_corners[:5,0],plot_corners[:5,2],plot_corners[:5,1],'-')
    ax.plot(plot_corners[5:,0],plot_corners[5:,2],plot_corners[5:,1],'-')
    
    for i in range(4):
        ax.plot([plot_corners[i,0], plot_corners[i+5,0]], [plot_corners[i,2], plot_corners[i+5,2]], [plot_corners[i,1], plot_corners[i+5,1]],'-')
    plt.show()
