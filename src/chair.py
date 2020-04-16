import part
import renderOpen3d
import numpy as np
import open3d as o3d
import random


class Back(part.Parts):
    def __init__(self, data_dir):
        super().__init__(data_dir, part.PartType.SEAT_BACK.value)


class Base(part.Parts):
    def __init__(self, data_dir):
        super().__init__(data_dir, part.PartType.SEAT_BASE.value)


class Leg(part.Parts):
    def __init__(self, data_dir):
        super().__init__(data_dir, part.PartType.SEAT_LEG.value)


class Arm(part.Parts):
    def __init__(self, data_dir):
        super().__init__(data_dir, part.PartType.SEAT_ARM.value)


class Chair:
    def __init__(self, data_dir):
        self._base = Base(data_dir)
        self._back = Back(data_dir)
        self._leg = Leg(data_dir)
        self._arm = Arm(data_dir)

    def render(self):
        render_sets = []
        for _parts in self.__iter__():
            render_sets += _parts.get_render_sets()
        o3d.visualization.draw_geometries(render_sets)

    def __iter__(self):
        return iter([self._base, self._back, self._leg, self._arm])

    def __str__(self):
        return '[{}]'.format(','.join(["{}".format(_parts) for _parts in self.__iter__()]))

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, _base):
        self._base = _base

    @property
    def back(self):
        return self._back

    @back.setter
    def back(self, _back):
        # scale
        yaabb_base = self.base.yaabb
        yaabb_back = _back.yaabb

        scale = (yaabb_base.obb.extent[0]) / ((yaabb_back.obb.extent[0]))
        _back.scale(scale)
        
        # find lowest farset point
       
        yaabb_back = _back.yaabb
        yaabb_base = self.base.yaabb

        intersect_vol = random.randrange(0, 10) * 1.0 / 100.0 # randomness
        
        d = yaabb_base.center - yaabb_back.center
        _back.translation(np.asarray([d[0], yaabb_base.y_max - yaabb_back.y_min - intersect_vol, d[1]]))

        points = np.vstack([_part.get_points() for _part in _back._parts])
        y_min = np.min(points[:, 1])
        z_min_back =  np.min(points[np.where(points[:, 1] == y_min)[0]][:, 2])

        points = np.vstack([_part.get_points() for _part in self.base._parts])
        y_max = np.max(points[:, 1])
        z_min_base =  np.min(points[np.where(points[:, 1] == y_max)[0]][:, 2])

        vol = random.randrange(0, 25) * 1.0 / 1000.0 # randomness
        _back.translation(np.asarray([0,0, z_min_base+vol-z_min_back]))
        self._back = _back

    @property
    def leg(self):
        return self._leg

    @leg.setter
    def leg(self, _leg):
        # scale
        yaabb_base = self.base.yaabb
        yaabb_leg = _leg.yaabb
        scale = (yaabb_base.obb.extent[0]*yaabb_base.obb.extent[2]) / ((yaabb_leg.obb.extent[0]*yaabb_leg.obb.extent[2]))
        _leg.scale(scale)

        yaabb_leg = _leg.yaabb
        # transition
        d = yaabb_base.center - yaabb_leg.center # (x,z)

        intersect_vol = 0.05 # make it random

        _leg.translation(np.asarray([d[0], yaabb_base.y_min - yaabb_leg.y_max + intersect_vol, d[1]]))
        self._leg = _leg

        # TODO: deformation

    @property
    def arm(self):
        return self._arm

    @arm.setter
    def arm(self, _arm):
        pass


if __name__ == "__main__":
    # import argparse
    # parser = argparse.ArgumentParser(description='test parser')
    # parser.add_argument('data_dir', type=str,                         
    #                     help='data dir, like partnet/1173')

    # args = parser.parse_args()
    
    # chair = Chair(args.data_dir)

    # print(chair)
    # chair.render()


    chair_1 = Chair("../../../partnet/Chair_parts/2585")
    # chair_1.render()

    chair_2 = Chair("../../../partnet/Chair_parts/2323")
    # chair_2.render()

    new_chair = Chair(None)
    new_chair.base = chair_1.base
    new_chair.leg = chair_2.leg
    new_chair.back = chair_2.back
    new_chair.render()




