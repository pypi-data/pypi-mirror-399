import re

import numpy as np

import homcloud.dipha as dipha
import homcloud.homccube as homccube


class PhatTwist:
    @staticmethod
    def find(filtration, name):
        if name == "phat-twist":
            return PhatTwist(filtration)

    def __init__(self, filtration):
        self.filtration = filtration

    def run(self, **_):
        matrix = self.filtration.build_phat_matrix()
        matrix.reduce_twist()
        return matrix.birth_death_pairs(), matrix.boundary_map_byte_sequence()


class PhatChunkParallel:
    @staticmethod
    def find(filtration, name):
        if name == "phat-chunk-parallel":
            return PhatChunkParallel(filtration)

    def __init__(self, filtration):
        self.filtration = filtration

    def run(self, **_):
        matrix = self.filtration.build_phat_matrix()
        matrix.reduce_chunk()
        return matrix.birth_death_pairs(), matrix.boundary_map_byte_sequence()


class Dipha:
    @staticmethod
    def find(filtration, name):
        if name == "dipha":
            return Dipha(filtration)

    def __init__(self, filtration):
        self.filtration = filtration

    def run(self, *, parallels=1, dual=False, upper_dim=None, upper_value=None):
        return dipha.pairs_from_filtration(self.filtration, parallels, dual, upper_dim, upper_value), None


class HomcCube:
    @staticmethod
    def find(filtration, name):
        if m := re.match(r"homccube-(\d+)", name):
            return HomcCube(filtration, int(m.group(1)))

    def __init__(self, filtration, threshold):
        self.filtration = filtration
        self.threshold = threshold

    def run(self, **_):
        assert self.filtration.dim in [2, 3]
        pairs = homccube.compute_pd(
            self.filtration.index_bitmap.astype(np.int32), self.filtration.periodicity, self.threshold
        )
        return pairs, None


def find_ph_routine(filtration, name):
    if name:
        for routine in filtration.supported_ph_routines():
            if r := routine.find(filtration, name):
                return r
        raise NotImplementedError("unknown PH routine: {}".format(name))
    else:
        return filtration.prefered_ph_routine()
