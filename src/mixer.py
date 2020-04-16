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
    def __init__(self, data_dir, output_dir):
        self.data_dir = data_dir
        self.chair_ids = os.listdir(data_dir)
        self.output_dir = output_dir

    def _sample(self):
        back = Parts('{}/{}'.format(self.data_dir, random.choice(self.chair_ids)), 0)
        seat = Parts('{}/{}'.format(self.data_dir, random.choice(self.chair_ids)), 1)
        leg = Parts('{}/{}'.format(self.data_dir, random.choice(self.chair_ids)), 2)
        armrest = Parts('{}/{}'.format(self.data_dir, random.choice(self.chair_ids)), 3)
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

        # scale back
        if back.num:
            back_obb = back._parts[0].obb
            x_scale = (seat_obb.get_max_bound()[0] - seat_obb.get_min_bound()[0])/(back_obb.get_max_bound()[0] - back_obb.get_min_bound()[0])
            back.scale(x_scale)
            # back should be attached to the seat
            back_obb = back._parts[0].obb
            z_offset = seat_obb.get_min_bound()[2] - back_obb.get_min_bound()[2]
            y_offset = seat_obb.get_max_bound()[1] - back_obb.get_min_bound()[1]
            back.translate([0, y_offset, z_offset])

        # scale leg
        if leg.num:
            leg_obb = leg._parts[0].obb
            x_scale = 0.8*(seat_obb.get_max_bound()[0] - seat_obb.get_min_bound()[0])/(leg_obb.get_max_bound()[0] - leg_obb.get_min_bound()[0])
            leg.scale(x_scale)
            # legs should be attached to the seat
            leg_obb = leg._parts[0].obb
            y_offset = seat_obb.get_min_bound()[1] - leg_obb.get_max_bound()[1]
            leg.translate([0, y_offset, 0])

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
    mixer = Mixer('../../Chair_parts/', "../output")
    chairs = mixer.generate(10, True)
    print('finished')

# %%
