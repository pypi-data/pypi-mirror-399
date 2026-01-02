import io

import pytest
import numpy as np
import msgpack

from homcloud.alpha_filtration import AlphaFiltration
from homcloud.pdgm_format import PDGMReader
from homcloud.pdgm import PDGM
import homcloud.cgal_info as cgal_info


def multiplicity_pd(path, dim, birth, death, epsilon=0.01):
    count = 0
    with PDGM.open(path, dim) as pdgm:
        for b, d in zip(pdgm.births, pdgm.deaths):
            if abs(b - birth) < epsilon and abs(d - death) < epsilon:
                count += 1
    return count


class TestAlphaFiltration:
    def test_build_phat_matrix(self, tetrahedron):
        filt = AlphaFiltration.create(tetrahedron, 3, save_boundary_map=True)
        matrix = filt.build_phat_matrix()
        bmap = msgpack.unpackb(matrix.boundary_map_byte_sequence(), raw=False)
        assert bmap == {
            "chunktype": "boundary_map",
            "type": "simplicial",
            "map": [
                [0, []],
                [0, []],
                [0, []],
                [0, []],
                [1, [1, 0]],
                [1, [3, 1]],
                [1, [3, 0]],
                [1, [3, 2]],
                [1, [1, 2]],
                [1, [0, 2]],
                [2, [5, 6, 4]],
                [2, [5, 7, 8]],
                [2, [4, 8, 9]],
                [2, [6, 7, 9]],
                [3, [10, 11, 13, 12]],
            ],
        }

    @pytest.mark.parametrize(
        "algorithm, save_bm, save_phtrees",
        [
            ("phat-twist", False, False),
            ("phat-twist", True, False),
            ("phat-twist", True, True),
            (None, False, False),
            (None, True, False),
            (None, True, True),
        ],
    )
    def test_compute_pdgm(self, tetrahedron, algorithm, save_bm, save_phtrees):
        symbols = ["X", "Y", "Z", "U"]
        filt = AlphaFiltration.create(tetrahedron, 3, False, None, True, symbols, save_bm, save_phtrees)
        f = io.BytesIO()
        filt.compute_pdgm(f, algorithm)
        f.seek(0)
        reader = PDGMReader(f)
        assert reader.metadata["dim"] == 3
        assert reader.metadata["filtration_type"] == "alpha"
        births, deaths, ess_births = reader.load_pd_chunk("pd", 0)
        assert births == [0, 0, 0]
        assert sorted(deaths) == [11.25, 13.25, 14.0]
        assert ess_births == [0]
        births, deaths, ess_births = reader.load_pd_chunk("pd", 1)
        assert births == [14.0, 15.25, 16.0]
        assert len(deaths) == 3
        assert ess_births == []
        births, deaths, ess_births = reader.load_pd_chunk("pd", 2)
        assert births == [19.600000000000005]
        assert deaths == [21.069444444444443]
        assert ess_births == []

        births, deaths, ess_births = reader.load_pd_chunk("indexed_pd", 0)
        assert sorted(births) == [1, 2, 3]
        assert sorted(deaths) == [4, 5, 7]
        assert ess_births == [0]
        births, deaths, ess_births = reader.load_pd_chunk("indexed_pd", 1)
        assert sorted(births) == [6, 8, 9]
        assert sorted(deaths) == [10, 11, 12]
        assert ess_births == []
        births, deaths, ess_births = reader.load_pd_chunk("indexed_pd", 2)
        assert births == [13]
        assert deaths == [14]
        assert ess_births == []

        index_to_level = reader.load_simple_chunk("index_to_level")
        assert len(index_to_level) == 15
        for i in range(15 - 1):
            assert index_to_level[i] <= index_to_level[i + 1]

        assert sorted(reader.load_simple_chunk("allpairs", 0)) == sorted(
            [
                [0, None],
                [1, 4],
                [2, 7],
                [3, 5],
            ]
        )
        assert sorted(reader.load_simple_chunk("allpairs", 1)) == sorted(
            [
                [6, 10],
                [8, 11],
                [9, 12],
            ]
        )
        assert sorted(reader.load_simple_chunk("allpairs", 2)) == sorted([[13, 14]])

        assert reader.load_simple_chunk("vertex_symbols") == ["X", "Y", "Z", "U"]
        assert np.allclose(reader.load_simple_chunk("vertex_coordintes"), tetrahedron)
        assert list(map(len, reader.load_simple_chunk("index_to_simplex"))) == [
            1,
            1,
            1,
            1,
            2,
            2,
            2,
            2,
            2,
            2,
            3,
            3,
            3,
            3,
            4,
        ]
        assert reader.load_chunk("alpha_information") == {
            "chunktype": "alpha_information",
            "num_vertices": 4,
            "periodicity": None,
            "weighted": False,
            "squared": True,
        }

        if save_bm:
            assert reader.load_boundary_map_chunk() == {
                "chunktype": "boundary_map",
                "type": "simplicial",
                "map": [
                    [0, []],
                    [0, []],
                    [0, []],
                    [0, []],
                    [1, [1, 0]],
                    [1, [3, 1]],
                    [1, [3, 0]],
                    [1, [3, 2]],
                    [1, [1, 2]],
                    [1, [0, 2]],
                    [2, [5, 6, 4]],
                    [2, [5, 7, 8]],
                    [2, [4, 8, 9]],
                    [2, [6, 7, 9]],
                    [3, [10, 11, 13, 12]],
                ],
            }
        else:
            assert reader.load_boundary_map_chunk() is None

        if save_phtrees:
            assert reader.load_simple_chunk("phtrees") == [[13, 14, np.inf]]
        else:
            assert reader.load_simple_chunk("phtrees") is None

    @pytest.mark.parametrize("noise", [False, True])
    def test_compute_pdgm_for_periodic_alpha_filtration(self, lattice_5x5x5, noise, tmpdir):
        if noise:
            lattice_5x5x5 += np.random.uniform(-1e-6, 1e-6, size=lattice_5x5x5.shape)

        filtration = AlphaFiltration.create(lattice_5x5x5, 3, False, [(-0.5, 4.5)] * 3, True, None, True)

        pdgmpath = str(tmpdir.join("sc.pdgm"))
        with open(pdgmpath, "wb") as f:
            filtration.compute_pdgm(f)
        assert multiplicity_pd(pdgmpath, 0, 0, 0.25) == 124
        assert multiplicity_pd(pdgmpath, 1, 0.25, 0.5) == 248
        assert multiplicity_pd(pdgmpath, 2, 0.5, 0.75) == 124

        with PDGM.open(pdgmpath, 0) as pdgm:
            assert pdgm.alpha_information == {
                "chunktype": "alpha_information",
                "num_vertices": 125,
                "periodicity": [[-0.5, 4.5]] * 3,
                "weighted": False,
                "squared": True,
            }

    @pytest.mark.skipif(cgal_info.numerical_version < 1050601000, reason="CGAL version < 5.6")
    def test_case_non_cubic_box(self, tmpdir):
        lattice_5x4x5 = np.array([(x, y, z) for z in range(5) for y in range(4) for x in range(5)], dtype=float)
        lattice_5x4x5 += np.random.uniform(-0.00001, 0.00001, size=(5 * 4 * 5, 3))
        filtration = AlphaFiltration.create(
            lattice_5x4x5, 3, False, [(-0.5, 4.5), (-0.5, 3.5), (-0.5, 4.5)], True, None, True
        )

        pdgmpath = str(tmpdir.join("sc.pdgm"))
        with open(pdgmpath, "wb") as f:
            filtration.compute_pdgm(f)

        assert multiplicity_pd(pdgmpath, 0, 0, 0.25) == 99
        assert multiplicity_pd(pdgmpath, 1, 0.25, 0.50) == 198
        assert multiplicity_pd(pdgmpath, 2, 0.5, 0.75) == 99

        with PDGM.open(pdgmpath, 0) as pdgm:
            assert pdgm.alpha_information == {
                "chunktype": "alpha_information",
                "num_vertices": 100,
                "periodicity": [[-0.5, 4.5], [-0.5, 3.5], [-0.5, 4.5]],
                "weighted": False,
                "squared": True,
            }

    def test_optimal_volume(self, lattice_5x5x5):
        import homcloud.interface as hc

        pdlist = hc.PDList.from_alpha_filtration(
            lattice_5x5x5 + np.random.uniform(-0.00001, 0.00001, size=lattice_5x5x5.shape),
            save_boundary_map=True,
            periodicity=([(-0.5, 4.5)] * 3),
        )
        pair = pdlist.dth_diagram(1).nearest_pair_to(0.26, 0.49)
        sv = pair.stable_volume(0.001)
        assert len(sv.boundary_points()) == 4
        assert len(sv.boundary()) == 4
        boundary = sv.boundary()
        for edge in boundary:
            p, q = edge
            d1, d2, d3 = np.sort(np.abs(np.array(p) - np.array(q)))
            assert d1 == pytest.approx(0, abs=0.001)
            assert d2 == pytest.approx(0, abs=0.001)
            assert d3 == pytest.approx(1, abs=0.001) or d3 == pytest.approx(4, abs=0.001)
