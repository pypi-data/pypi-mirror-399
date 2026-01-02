import numpy as np
import ripser

from homcloud.pdgm_format import (
    PDGMWriter,
    PDChunk,
    BoundaryMapChunk,
    RipsInformationChunk,
    GraphWeightsChunk,
)
import homcloud.phat_ext as phat


class DistanceMatrix:
    def __init__(self, matrix, upper_dim, upper_value=np.inf, vertex_symbols=None):
        assert matrix.ndim == 2 and matrix.shape[0] == matrix.shape[1]
        self.matrix = matrix
        self.upper_dim = upper_dim
        self.upper_value = upper_value
        self.vertex_symbols = vertex_symbols

    def build_rips_filtration(self, save_graph=False, save_cocycle=False):
        return RipsFiltration(
            self.matrix.astype(np.float32), self.upper_dim, self.upper_value, save_graph, save_cocycle
        )

    def build_simplicial_filtration(self, save_boundary_map=False):
        simplices = sorted(self.all_simplices(), key=lambda x: (x[0], len(x[1])))
        index_to_level = [level for (level, simplex) in simplices]
        index_to_simplex = [simplex for (level, simplex) in simplices]
        simplex_to_index = {simplex: index for (index, (value, simplex)) in enumerate(simplices)}
        if self.vertex_symbols is None:
            vertex_symbols = [str(k) for k in range(self.matrix.shape[0])]
        else:
            vertex_symbols = self.vertex_symbols

        return SimplicialFiltration(
            self, index_to_level, index_to_simplex, simplex_to_index, vertex_symbols, save_boundary_map
        )

    def all_simplices(self):
        npoints = self.matrix.shape[0]

        def value_of_simplex(simplex, i, value):
            return max(np.max(self.matrix[i, simplex]), value)

        def iter(simplex, value):
            if len(simplex) > self.upper_dim + 1:
                return

            for i in range(simplex[-1] + 1, npoints):
                newvalue = value_of_simplex(simplex, i, value)
                if newvalue >= self.upper_value:
                    continue
                simplex.append(i)
                yield newvalue, tuple(simplex)
                yield from iter(simplex, newvalue)
                simplex.pop()

        for i in range(npoints):
            yield (0.0, (i,))
            yield from iter([i], -np.inf)


class RipsFiltration:
    def __init__(self, matrix, upper_dim, upper_value, save_graph, save_cocycle):
        self.matrix = matrix
        self.upper_dim = upper_dim
        self.upper_value = upper_value
        self.save_graph = save_graph
        self.save_cocycle = save_cocycle

    def compute_pdgm(self, f, algorithm=None, save_suppl_info=True, parallels=None):
        assert algorithm is None or algorithm == "ripser"
        self.compute_pdgm_by_ripser(f)

    def compute_pdgm_by_ripser(self, f):
        def build_pdchunk(d, pairs):
            births = []
            deaths = []
            ess_births = []
            for k in range(pairs.shape[0]):
                birth = pairs[k, 0]
                death = pairs[k, 1]
                if death == np.inf:
                    ess_births.append(birth)
                else:
                    births.append(birth)
                    deaths.append(death)
            return PDChunk("pd", d, births, deaths, ess_births)

        diagrams = ripser.ripser(
            self.matrix,
            self.upper_dim,
            self.upper_value,
            2,  # Z/2Z
            True,  # The first argument is a distane matrix, not a pointcloud
            do_cocycles=self.save_cocycle,
        )

        writer = PDGMWriter(f, "rips", self.upper_dim + 1)

        for d, pairs in enumerate(diagrams["dgms"]):
            writer.append_chunk(build_pdchunk(d, pairs))

        self.append_rips_information_chunk(writer)
        self.append_graph_weights_chunk(writer)

        if self.save_cocycle:
            self.append_cocycle_chunk(writer, diagrams["dgms"], diagrams["cocycles"])

        writer.write()

    def append_graph_weights_chunk(self, writer):
        if not self.save_graph:
            return
        writer.append_chunk(GraphWeightsChunk(self.matrix))

    def append_rips_information_chunk(self, writer):
        writer.append_chunk(RipsInformationChunk(self.num_vertices))

    def append_cocycle_chunk(self, writer, dgms, cocycles):
        for d in range(len(dgms)):
            writer.append_simple_chunk(
                "cocycles", [cocycle.tolist() for (cocycle, pair) in zip(cocycles[d], dgms[d]) if pair[1] != np.inf], d
            )

    @property
    def num_vertices(self):
        return self.matrix.shape[0]


class SimplicialFiltration:
    def __init__(
        self, dmatrix, index_to_level, index_to_simplex, simplex_to_index, vertex_symbols, save_boundary_map=False
    ):
        self.distance_matrix = dmatrix
        self.index_to_level = index_to_level
        self.index_to_simplex = index_to_simplex
        self.simplex_to_index = simplex_to_index
        self.vertex_symbols = vertex_symbols
        self.boundary_map = self.build_boundary_map()
        self.save_boundary_map = save_boundary_map

    def build_boundary_map(self):
        def boundary(simplex):
            if len(simplex) == 1:
                return

            for k in range(len(simplex)):
                key = simplex[:k] + simplex[k + 1 :]
                yield self.simplex_to_index[key]

        return [[len(simplex) - 1, list(boundary(simplex))] for simplex in self.index_to_simplex]

    @property
    def upper_dim(self):
        return self.distance_matrix.upper_dim

    def build_phat_matrix(self):
        phat_matrix = phat.Matrix(len(self.index_to_simplex), "none")
        for index, (dim, col) in enumerate(self.boundary_map):
            phat_matrix.set_dim_col(index, dim, col)

        return phat_matrix

    def compute_pdgm(self, f, algorithm=None, save_suppl_info=True, parallels=None):
        assert save_suppl_info

        phat_matrix = self.build_phat_matrix()
        phat_matrix.reduce(algorithm)
        writer = PDGMWriter(f, "simplicial", self.upper_dim + 1)
        writer.save_pairs(phat_matrix.birth_death_pairs(), self.index_to_level)
        writer.append_simple_chunk("index_to_level", self.index_to_level)
        writer.append_simple_chunk("index_to_simplex", self.index_to_simplex)
        writer.append_simple_chunk("vertex_symbols", self.vertex_symbols)
        if self.save_boundary_map:
            writer.append_chunk(BoundaryMapChunk("simplicial", self.boundary_map))

        writer.write()
