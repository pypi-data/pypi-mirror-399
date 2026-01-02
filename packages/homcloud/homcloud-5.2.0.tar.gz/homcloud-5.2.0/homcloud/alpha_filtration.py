import math

import msgpack
import numpy as np

from homcloud.pdgm_format import PDGMWriter, BinaryChunk, AlphaInformationChunk
import homcloud.phat_ext as phat
import homcloud.build_phtrees as build_phtrees
import homcloud.alpha_shape3_ext as alpha_shape3_ext
import homcloud.periodic_alpha_shape3_ext as periodic_alpha_shape3_ext
import homcloud.alpha_shape2_ext as alpha_shape2_ext
import homcloud.periodic_alpha_shape2_ext as periodic_alpha_shape2_ext


def compute_simplex_alpha_pairs(points, dim, weighted, periodicity):
    match (dim, periodicity):
        case (2, None):
            compute = alpha_shape2_ext.compute
        case (2, _):
            compute = periodic_alpha_shape2_ext.compute
        case (3, None):
            compute = alpha_shape3_ext.compute
        case (3, _):
            compute = periodic_alpha_shape3_ext.compute
        case _:
            raise ValueError("data dimension should be 2 or 3")

    flatten_periodicity = [] if periodicity is None else np.array(periodicity).ravel().tolist()
    return compute(points, weighted, *flatten_periodicity)


def boundary_of_simplex(s):
    if len(s) == 1:
        return []
    else:
        return [s[:n] + s[n + 1 :] for n in range(len(s))]


class AlphaFiltration:
    @staticmethod
    def create(
        points,
        dim,
        weighted=False,
        periodicity=None,
        squared=True,
        symbols=None,
        save_boundary_map=False,
        save_phtrees=False,
    ):
        coordinates = points[:, :dim]
        weights = points[:, -1] if weighted else None
        simplex_alpha_pairs = compute_simplex_alpha_pairs(points, dim, weighted, periodicity)
        return AlphaFiltration(
            coordinates,
            weights,
            dim,
            simplex_alpha_pairs,
            periodicity,
            squared,
            symbols,
            save_boundary_map,
            save_phtrees,
        )

    def __init__(
        self,
        coordinates,
        weights,
        dim,
        simplex_alpha_pairs,
        periodicity,
        squared,
        symbols,
        save_boundary_map,
        save_phtrees,
    ):
        def sortkey(simplex_alpha_pair):
            simplex, alpha = simplex_alpha_pair
            return (alpha, len(simplex))

        def normalize_alpha(alpha):
            return alpha if squared else math.copysign(math.sqrt(abs(alpha)), alpha)

        self.coordinates = coordinates
        self.weights = weights
        self.dim = dim
        self.periodicity = periodicity
        self.squared = squared
        self.symbols = symbols
        self.save_boundary_map = save_boundary_map
        self.save_phtrees = save_phtrees
        self.index_to_simplex = []
        self.index_to_level = []
        self.simplex_to_index = {}

        for index, (simplex, alpha) in enumerate(sorted(simplex_alpha_pairs, key=sortkey)):
            self.index_to_simplex.append(simplex)
            self.index_to_level.append(normalize_alpha(alpha))
            self.simplex_to_index[simplex] = index

    def compute_pdgm(self, f, algorithm=None, output_suppl_info=True, parallels=None):
        writer = PDGMWriter(f, "alpha", self.dim)

        matrix = self.build_phat_matrix()
        matrix.reduce(algorithm)

        writer.save_pairs(matrix.birth_death_pairs(), self.index_to_level, output_suppl_info)
        writer.append_chunk(self.alpha_information_chunk())

        if output_suppl_info:
            writer.append_simple_chunk("index_to_level", self.index_to_level)
            writer.append_simple_chunk("vertex_symbols", self.symbols)
            writer.append_simple_chunk("vertex_coordintes", self.coordinates.tolist())
            writer.append_simple_chunk("index_to_simplex", self.index_to_simplex)

        if self.save_boundary_map:
            writer.append_chunk(BinaryChunk("boundary_map", matrix.boundary_map_byte_sequence()))
        if self.save_phtrees:
            boundary_map = msgpack.unpackb(matrix.boundary_map_byte_sequence(), raw=False).get("map")
            writer.append_simple_chunk("phtrees", self.build_phtrees(boundary_map).to_list())

        writer.write()

    def build_phat_matrix(self):
        boundary_of = boundary_of_simplex

        matrix = phat.Matrix(self.num_simplices(), self.boundary_map_style())
        for index, simplex in enumerate(self.index_to_simplex):
            dim_simplex = len(simplex) - 1
            matrix.set_dim_col(index, dim_simplex, [self.simplex_to_index[t] for t in boundary_of(simplex)])

        return matrix

    def num_simplices(self):
        return len(self.index_to_simplex)

    def boundary_map_style(self):
        return "simplicial" if self.save_boundary_map else "none"

    def alpha_information_chunk(self):
        return AlphaInformationChunk(self.coordinates.shape[0], self.periodicity, self.weighted, self.squared)

    @property
    def weighted(self):
        return self.weights is not None

    def build_phtrees(self, boundary_map):
        return build_phtrees.PHTrees(self.dim, boundary_map)
