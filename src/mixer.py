# %%
import os
import json
from enum import Enum
from pyobb.obb import OBB
import numpy as np
import renderOpen3d
import open3d as o3d
from part import Parts, Part
import random
import util

class Mixer:
    def __init__(self, data_dir, output_dir, chair_ids=None):
        self.data_dir = data_dir
        self.chair_ids = chair_ids
        self.output_dir = output_dir
        if self.chair_ids is None:
            self.chair_ids = os.listdir(data_dir)

    def _sample(self):
        back = Parts('{}/{}'.format(self.data_dir, random.choice(self.chair_ids)), 0)
        seat = Parts('{}/{}'.format(self.data_dir, random.choice(self.chair_ids)), 1)
        leg = Parts('{}/{}'.format(self.data_dir, random.choice(self.chair_ids)), 2)
        #armrest = Parts('{}/{}'.format(self.data_dir, random.choice(self.chair_ids)), 3)
        armrest = Parts(back.data_dir, 3)
        return back, seat, leg, armrest

    def _make_chair(self, parts_list):
        chair = Parts(None, 4)
        for parts in parts_list:
            for part in parts._parts:
               chair._parts.append(part) 
        chair.num = len(parts_list)
        return chair

    def _mix(self, back, seat, leg, armrest):
        parts_list = [back, seat, leg, armrest]
        # merge parts to create better aabb
        for parts in parts_list:
            parts.merge()

        seat_obb = seat._parts[0].obb

        if back.num:
            # scale back
            back_obb = back._parts[0].obb
            x_scale = (seat_obb.get_max_bound()[0] - seat_obb.get_min_bound()[0])/(back_obb.get_max_bound()[0] - back_obb.get_min_bound()[0])
            back.scale(x_scale)
            # back should be attached to the seat
            back_obb = back._parts[0].obb
            z_offset = seat_obb.get_min_bound()[2] - back_obb.get_min_bound()[2]
            z_offset -= random.uniform(0,0.6)*(back_obb.get_max_bound()[2]-back_obb.get_min_bound()[2])
            y_offset = seat_obb.get_max_bound()[1] - back_obb.get_min_bound()[1]
            y_offset -= random.uniform(0,0.03)
            back.translate([0, y_offset, z_offset])
            if armrest.num:
                armrest.scale(x_scale)
                armrest.translate([0, y_offset, z_offset])
        else:
            armrest.num = 0 # disable armrest when no back is found, because we don't know where to put it

        if leg.num:
            # scale leg
            leg_obb = leg._parts[0].obb
            x_scale = random.uniform(0.6, 0.9)*(seat_obb.get_max_bound()[0] - seat_obb.get_min_bound()[0])/(leg_obb.get_max_bound()[0] - leg_obb.get_min_bound()[0])
            leg.scale(x_scale)
            # legs should be attached to the seat
            leg_obb = leg._parts[0].obb
            y_offset = seat_obb.get_min_bound()[1] - leg_obb.get_max_bound()[1]
            y_offset += random.uniform(0,0.03)
            leg.translate([0, y_offset, 0])
        '''
        if armrest.num:
            # scale armrest
            origin_back = Parts(armrest.data_dir, 0)
            origin_back.merge()
            origin_back_obb = origin_back._parts[0].obb
            x_scale = (seat_obb.get_max_bound()[0] - seat_obb.get_min_bound()[0])/(origin_back_obb.get_max_bound()[0] - origin_back_obb.get_min_bound()[0])
            origin_back.scale(x_scale)
            armrest.scale(x_scale)
            # armrest should be attached to the back
            origin_back_obb = origin_back._parts[0].obb
            z_offset = seat_obb.get_min_bound()[2] - origin_back_obb.get_min_bound()[2]
            y_offset = seat_obb.get_max_bound()[1] - origin_back_obb.get_min_bound()[1]
            armrest.translate([0, y_offset, z_offset])
        '''

        chair = self._make_chair(parts_list)
        return chair
    
    def _save(self, chair, id):
        chair.merge()
        part = chair._parts[0]
        util.export_obj("{}/{}.obj".format(self.output_dir, id), part.v, part.f, [0.216, 0.494, 0.722])

    def generate(self, cnt=1, write_to_disk=False):
        chairs = []
        for i in range(cnt):
            back, seat, leg, armrest = self._sample()
            chair = self._mix(back, seat, leg, armrest)
            if write_to_disk:
                self._save(chair, i)
            else:
                chairs.append(chair)
        return chairs


if __name__ == "__main__": 
    mixer = Mixer('../../Chair_parts/', "../output/a", chair_ids = [2585, 2323, 43872])
    mixer.generate(10, True)
    mixer = Mixer('../../Chair_parts/', "../output/b", chair_ids = [39055, 37529, 40096, 41975, 37546])
    mixer.generate(30, True)
    mixer = Mixer('../../Chair_parts/', "../output/c", chair_ids = [37107, 39781, 40141, 39426, 35698, 2320, 40546, 37790, 43006, 37108])
    mixer.generate(100, True)
    mixer = Mixer('../../Chair_parts/', "../output/c", chair_ids = [40141])
    print('finished')

# %%
