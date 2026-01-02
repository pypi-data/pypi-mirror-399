import math

import numpy as np

import homcloud.coupled_alpha_ext as coupled_alpha_ext
import homcloud.phat_ext as phat
from homcloud.pdgm_format import PDGMWriter, BoundaryMapChunk, CoupledAlphaRelativeInformationChunk
from homcloud.alpha_filtration import boundary_of_simplex as boundary_of


class CoupledAlphaShape:
    @staticmethod
    def build(X, Y):
        X = X.astype(np.float64)
        Y = Y.astype(np.float64)
        dim = X.shape[1]
        if dim == 2:
            filtration_values = coupled_alpha_ext.compute_2d(X, Y)
        elif dim == 3:
            filtration_values = coupled_alpha_ext.compute_3d(X, Y)
        else:
            raise ValueError("Dimension of the pair of pointclouds should be 2 or 3")

        return CoupledAlphaShape(X, Y, filtration_values)

    def __init__(self, X, Y, filtration_values):
        self.X = X
        self.Y = Y
        self.filtration_values = filtration_values

    @property
    def dim(self):
        return self.X.shape[1]

    def relative_ph_filtration(self, squared=True, symbols=None, save_boundary_map=False):
        def is_upper_simplex(simplex):
            return any(vertex >= self.X.shape[0] for vertex in simplex)

        def adjust_level(value):
            return value if squared else math.sqrt(value)

        simplices = [s for s in self.filtration_values if is_upper_simplex(s)]
        simplices.sort(key=lambda s: self.filtration_values[s])
        simplex_to_index = {s: n for (n, s) in enumerate(simplices)}
        index_to_level = [adjust_level(self.filtration_values[s]) for s in simplices]
        points = np.vstack([self.X, self.Y])
        labels = [0] * self.X.shape[0] + [1] * self.Y.shape[0]

        return RelativePHFiltration(
            points, labels, squared, simplices, simplex_to_index, index_to_level, symbols, save_boundary_map
        )


class RelativePHFiltration:
    def __init__(
        self, points, labels, squared, simplices, simplex_to_index, index_to_level, symbols, save_boundary_map
    ):
        self.points = points
        self.labels = labels
        self.squared = squared
        self.simplices = simplices
        self.simplex_to_index = simplex_to_index
        self.index_to_level = index_to_level
        self.symbols = symbols
        self.save_boundary_map = save_boundary_map

    @property
    def dim(self):
        return self.points.shape[1]

    def compute_pdgm(self, f, algorithm=None, output_suppl_info=True, parallels=None):
        writer = PDGMWriter(f, "coupled-alpha-relative", self.dim)

        matrix = self.build_phat_matrix()
        matrix.reduce(algorithm)

        writer.save_pairs(matrix.birth_death_pairs(), self.index_to_level, output_suppl_info)
        writer.append_chunk(self.coupled_alpha_relative_information_chunk())

        if output_suppl_info:
            writer.append_simple_chunk("index_to_level", self.index_to_level)
            writer.append_simple_chunk("vertex_symbols", self.symbols)
            writer.append_simple_chunk("vertex_coordintes", self.points.tolist())
            writer.append_simple_chunk("vertex_lavels", self.labels)
            writer.append_simple_chunk("index_to_simplex", [list(s) for s in self.simplices])

        if self.save_boundary_map:
            writer.append_chunk(BoundaryMapChunk("abstract", self.boundary_map()))

        writer.write()

    def build_phat_matrix(self):
        matrix = phat.Matrix(len(self.simplices), "none")
        for simplex in self.simplices:
            boundary_on = [self.simplex_to_index[b] for b in boundary_of(simplex) if b in self.simplex_to_index]
            matrix.set_dim_col(self.simplex_to_index[simplex], len(simplex) - 1, boundary_on)

        return matrix

    def coupled_alpha_relative_information_chunk(self):
        x_size = sum(self.labels)
        y_size = len(self.labels) - x_size
        return CoupledAlphaRelativeInformationChunk(x_size, y_size, self.squared)

    def boundary_map(self):
        def signed_boundary(simplex):
            on = []
            signs = []
            for n, b in enumerate(boundary_of(simplex)):
                if b in self.simplex_to_index:
                    on.append(self.simplex_to_index[b])
                    signs.append(1 if n % 2 == 0 else -1)
            return [len(simplex) - 1, on, signs]

        return [signed_boundary(simplex) for simplex in self.simplices]
