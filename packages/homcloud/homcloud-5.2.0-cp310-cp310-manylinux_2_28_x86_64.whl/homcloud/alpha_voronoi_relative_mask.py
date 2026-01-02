import math

import numpy as np
from cached_property import cached_property

from homcloud.alpha_filtration import compute_simplex_alpha_pairs, boundary_of_simplex as boundary_of
from homcloud.pdgm_format import PDGMWriter, BoundaryMapChunk, AlphaVoronoiRelativeMaskInformationChunk
import homcloud.phat_ext as phat


class AlphaVoronoiRelativeMaskFiltration:
    @staticmethod
    def create(
        points, mask_points, dim, weighted=False, periodicity=None, squared=True, symbols=None, save_boundary_map=False
    ):
        npoints = points.shape[0]

        def ismasksimplex(simplex):
            return all(v >= npoints for v in simplex)

        coordinates = points[:, :dim]
        mask_coordinates = mask_points[:, :dim]
        weights = points[:, -1] if weighted else None
        mask_weights = mask_points[:, -1] if weighted else None

        simplex_alpha_pairs = compute_simplex_alpha_pairs(np.vstack([points, mask_points]), dim, weighted, periodicity)
        simplex_alpha_pairs = [
            (simplex, alpha) for simplex, alpha in simplex_alpha_pairs if not ismasksimplex(simplex)
        ]

        return AlphaVoronoiRelativeMaskFiltration(
            coordinates,
            mask_coordinates,
            weights,
            mask_weights,
            simplex_alpha_pairs,
            periodicity,
            squared,
            symbols,
            save_boundary_map,
        )

    def __init__(
        self,
        coordinates_main,
        coordinates_mask,
        weights_main,
        weights_mask,
        simplex_alpha_pairs,
        periodicity,
        squared,
        symbols,
        save_boundary_map,
    ):
        def sortkey(simplex_alpha_pair):
            simplex, alpha = simplex_alpha_pair
            return (alpha, len(simplex), simplex)

        def normalize_alpha(a):
            return a if squared else math.sqrt(a)

        self.coordinates_main = coordinates_main
        self.coordinates_mask = coordinates_mask
        self.weights_main = weights_main
        self.weights_mask = weights_mask
        self.periodicity = periodicity
        self.squared = squared
        self.symbols = symbols
        self.save_boundary_map = save_boundary_map

        self.index_to_simplex = []
        self.index_to_level = []
        self.simplex_to_index = {}

        for index, (simplex, alpha) in enumerate(sorted(simplex_alpha_pairs, key=sortkey)):
            self.index_to_simplex.append(simplex)
            self.index_to_level.append(normalize_alpha(alpha))
            self.simplex_to_index[simplex] = index

    def compute_pdgm(self, f, algorithm=None, output_suppl_info=True, parallels=None):
        writer = PDGMWriter(f, "alpha-voronoi-relative-mask", self.dim)

        matrix = self.build_phat_matrix()
        matrix.reduce(algorithm)

        writer.save_pairs(matrix.birth_death_pairs(), self.index_to_level, output_suppl_info)
        writer.append_chunk(self.alpha_voronoi_relative_mask_information_chunk())

        if output_suppl_info:
            writer.append_simple_chunk("index_to_level", self.index_to_level)
            writer.append_simple_chunk("vertex_symbols", self.symbols)
            writer.append_simple_chunk("vertex_coordintes", self.coordinates.tolist())
            writer.append_simple_chunk("index_to_simplex", self.index_to_simplex)

        if self.save_boundary_map:
            writer.append_chunk(BoundaryMapChunk("abstract", self.boundary_map))

        writer.write()

    def build_phat_matrix(self):
        matrix = phat.Matrix(self.num_simplices, "none")
        for index, (dim, b, _) in enumerate(self.boundary_map):
            matrix.set_dim_col(index, dim, b)
        return matrix

    @property
    def coordinates(self):
        return np.vstack([self.coordinates_main, self.coordinates_mask])

    @property
    def dim(self):
        return self.coordinates_main.shape[1]

    @property
    def num_simplices(self):
        return len(self.index_to_simplex)

    @cached_property
    def boundary_map(self):
        def signed_boundary(simplex):
            on = []
            signs = []
            for n, b in enumerate(boundary_of(simplex)):
                if b in self.simplex_to_index:
                    on.append(self.simplex_to_index[b])
                    signs.append(1 if n % 2 == 0 else -1)
            return [len(simplex) - 1, on, signs]

        return [signed_boundary(simplex) for simplex in self.index_to_simplex]

    def alpha_voronoi_relative_mask_information_chunk(self):
        return AlphaVoronoiRelativeMaskInformationChunk(
            self.coordinates_main.shape[0],
            self.coordinates_mask.shape[0],
            self.periodicity,
            self.weighted,
            self.squared,
        )

    @property
    def weighted(self):
        return self.weights_main is not None
