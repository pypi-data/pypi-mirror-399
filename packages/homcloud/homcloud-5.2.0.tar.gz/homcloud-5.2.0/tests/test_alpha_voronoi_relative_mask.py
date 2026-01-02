import io

import numpy as np
import pytest

from homcloud.alpha_voronoi_relative_mask import AlphaVoronoiRelativeMaskFiltration
from homcloud.pdgm_format import PDGMReader
from tests.helper import minimal_squared_circumradius


class TestAlphaVoronoiRelativeMaskFiltration:
    def test_boundary_map(self, pc_avrm_2d_pair):
        filt = AlphaVoronoiRelativeMaskFiltration.create(*pc_avrm_2d_pair, 2, save_boundary_map=True)
        assert filt.boundary_map == [
            [0, [], []],
            [0, [], []],
            [1, [1, 0], [1, -1]],
            [1, [0], [-1]],
            [1, [1], [-1]],
            [1, [1], [-1]],
            [2, [5, 3, 2], [1, -1, 1]],
            [2, [5, 4], [-1, 1]],
        ]

    def test_build_phat_matrix(self, pc_avrm_2d_pair):
        filt = AlphaVoronoiRelativeMaskFiltration.create(*pc_avrm_2d_pair, 2, save_boundary_map=True)
        matrix = filt.build_phat_matrix()
        matrix.reduce_twist()
        assert sorted(matrix.birth_death_pairs()) == sorted([(0, 1, 2), (0, 0, 3), (1, 5, 6), (1, 4, 7)])

    def test_compute_pdgm(self, pc_avrm_2d_pair):
        coordinates_all = np.vstack(pc_avrm_2d_pair)
        filt = AlphaVoronoiRelativeMaskFiltration.create(*pc_avrm_2d_pair, 2, save_boundary_map=True)
        f = io.BytesIO()
        filt.compute_pdgm(f)
        f.seek(0)
        reader = PDGMReader(f)
        assert reader.metadata["dim"] == 2
        assert reader.metadata["filtration_type"] == "alpha-voronoi-relative-mask"

        alpha_voronoi_relative_mask_information = reader.load_chunk("alpha_voronoi_relative_mask_information")
        assert alpha_voronoi_relative_mask_information["num_vertices_main"] == 2
        assert alpha_voronoi_relative_mask_information["num_vertices_mask"] == 2
        assert alpha_voronoi_relative_mask_information["periodicity"] is None
        assert not alpha_voronoi_relative_mask_information["weighted"]
        assert alpha_voronoi_relative_mask_information["squared"]

        births, deaths, ess_births = reader.load_pd_chunk("pd", 0)
        assert births == pytest.approx([0, 0])
        assert deaths == pytest.approx([13 / 4, 18 / 4])
        assert ess_births == []

        births, deaths, ess_births = reader.load_pd_chunk("pd", 1)
        assert births == pytest.approx([25 / 4, 20 / 4])
        r1 = minimal_squared_circumradius(coordinates_all[[0, 1, 3], :])
        r2 = minimal_squared_circumradius(coordinates_all[[1, 2, 3], :])
        assert deaths == pytest.approx([r1, r2])
        assert ess_births == []

        assert ([], [], []) == reader.load_pd_chunk("pd", 2)

        assert (None, None, None) == reader.load_pd_chunk("pd", 3)

        births, deaths, ess_births = reader.load_pd_chunk("indexed_pd", 0)
        assert sorted(births) == [0, 1]
        assert sorted(deaths) == [2, 3]
        assert ess_births == []

        births, deaths, ess_births = reader.load_pd_chunk("indexed_pd", 1)
        assert sorted(births) == [4, 5]
        assert sorted(deaths) == [6, 7]
        assert ess_births == []

        index_to_simplex = reader.load_simple_chunk("index_to_simplex")
        assert index_to_simplex == [
            [
                0,
            ],
            [
                1,
            ],
            [0, 1],
            [0, 3],
            [1, 2],
            [1, 3],
            [0, 1, 3],
            [1, 2, 3],
        ]

        assert reader.load_simple_chunk("vertex_coordintes") == pytest.approx(coordinates_all)
