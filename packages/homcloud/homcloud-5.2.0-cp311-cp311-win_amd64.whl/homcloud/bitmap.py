import struct

import numpy as np
from cached_property import cached_property

from homcloud.pict.utils import nd_indices
from homcloud.cubical_ext import CubicalFiltrationExt
from homcloud.pdgm_format import PDGMWriter, SimpleChunk, BitmapInformationChunk, BinaryChunk
from homcloud.delegate import forwardable
import homcloud.ph_routine as ph_routine


class Bitmap:
    def __init__(self, array, flip_levels_sign=False, periodicity=None, save_boundary_map=False):
        assert array.size < 0x7FFF_FFFF
        self.array = array
        self.flip_levels_sign = flip_levels_sign
        self.periodicity = periodicity or [False] * array.ndim
        self.save_boundary_map = save_boundary_map

    def build_bitmap_filtration(self):
        indices = nd_indices(self.array.shape)
        keys = np.argsort(self.array, axis=None, kind="mergesort")
        index_to_level = self.sign * self.array.flatten()[keys]
        index_bitmap = invert_permutation(keys).reshape(self.array.shape)
        return BitmapFiltration(
            index_bitmap, self.periodicity, index_to_level, indices[keys, :], self.flip_levels_sign
        )

    def build_cubical_filtration(self):
        cubefilt_ext = CubicalFiltrationExt(self.array.astype(float), self.periodicity, self.save_boundary_map)
        return CubicalFiltration(cubefilt_ext, self.flip_levels_sign)

    def build_filtration(self, cubical):
        if cubical:
            return self.build_cubical_filtration()
        else:
            return self.build_bitmap_filtration()

    @property
    def sign(self):
        return -1 if self.flip_levels_sign else 1


class BitmapFiltration:
    def __init__(self, index_bitmap, periodicity, index_to_level, index_to_pixel, sign_flipped):
        self.index_bitmap = index_bitmap
        self.periodicity = periodicity
        self.index_to_level = index_to_level
        self.index_to_pixel = index_to_pixel
        self.sign_flipped = sign_flipped
        self.dim = index_bitmap.ndim

    def write_dipha_complex(self, f):
        """Write a picture to f with the dipha format."""
        if any(self.periodicity):
            raise NotImplementedError("dipha does not support periodic bitmap")

        f.write(struct.pack("qq", 8067171840, 1))
        f.write(struct.pack("qq", self.index_bitmap.size, self.dim))
        for g in reversed(self.index_bitmap.shape):
            f.write(struct.pack("q", g))

        for pixel in self.index_bitmap.flatten():
            f.write(struct.pack("d", pixel))

    def compute_pdgm(self, f, algorithm=None, save_suppl_info=True, parallels=1):
        writer = PDGMWriter(f, "bitmap", self.dim)
        writer.sign_flipped = self.sign_flipped
        pairs, _ = ph_routine.find_ph_routine(self, algorithm).run(parallels=parallels)
        writer.save_pairs(pairs, self.index_to_level, save_suppl_info)

        if save_suppl_info:
            writer.append_chunk(SimpleChunk("index_to_level", list(self.index_to_level)))
            writer.append_chunk(SimpleChunk("index_to_pixel", self.index_to_pixel.tolist()))
            writer.append_chunk(BitmapInformationChunk(self.index_bitmap.shape, self.periodicity))
        writer.write()

    @staticmethod
    def supported_ph_routines():
        return [ph_routine.HomcCube, ph_routine.Dipha]

    def prefered_ph_routine(self):
        if self.dim in [2, 3]:
            return ph_routine.HomcCube(self, 1)
        else:
            return ph_routine.Dipha(self)


def invert_permutation(a):
    """Create the inverse of the permutation given by a.

    If a is not a permutation, the result is indefinite.
    """
    s = np.zeros(a.size, dtype=np.float64)
    i = np.arange(a.size, dtype=np.int32)
    np.put(s, a, i)
    return s


@forwardable
class CubicalFiltration:
    __delegator_definitions__ = {"cubefilt_ext": ["value_at", "encode_cube", "decode_cube", "all_cubes"]}

    def __init__(self, cubefilt_ext, sign_flipped):
        self.cubefilt_ext = cubefilt_ext
        self.sign_flipped = sign_flipped

    @property
    def dim(self):
        return self.cubefilt_ext.array.ndim

    @property
    def shape(self):
        return self.cubefilt_ext.array.shape

    @property
    def periodicity(self):
        return self.cubefilt_ext.periodicity

    @property
    def index_bitmap(self):
        return self.cubefilt_ext.array

    @cached_property
    def index_to_level(self):
        sign = (-1) ** int(self.sign_flipped)
        return sign * self.cubefilt_ext.levels()

    @property
    def index_to_cube(self):
        return self.cubefilt_ext.sorted_cubes

    def build_phat_matrix(self):
        return self.cubefilt_ext.build_phat_matrix()

    def write_dipha_complex(self, output):
        output.write(self.cubefilt_ext.dipha_byte_sequence())

    def compute_pdgm(self, f, algorithm=None, save_suppl_info=True, parallels=None):
        writer = PDGMWriter(f, "cubical", self.dim)

        matrix = self.build_phat_matrix()
        matrix.reduce(algorithm)

        writer.save_pairs(matrix.birth_death_pairs(), self.index_to_level, save_suppl_info)

        if save_suppl_info:
            writer.append_simple_chunk("index_to_level", self.index_to_level.tolist())
            writer.append_simple_chunk("index_to_cube", self.index_to_cube)
            writer.append_chunk(BitmapInformationChunk(self.shape, self.periodicity))
        if boundary_map_byte_sequence := matrix.boundary_map_byte_sequence():
            writer.append_chunk(BinaryChunk("boundary_map", boundary_map_byte_sequence))
        writer.write()
