import io

import pytest

from homcloud.abstract_filtration import AbstractFiltrationLoader, AbstractFiltration
from homcloud.pdgm_format import PDGMReader


CODE1 = """
# comment
# id dim time = indices : coefs
0 0 0.0 = :
1 0 0.0 = :
2 1 1.0 = 0 1 : 1 -1
3 0 1.2 = :
4 1 1.3 = 1 3 : 1 -1
5 1 1.3 = 3 0 : 1 -1
6 2 2.1 = 2 4 5 : 1 1 1
"""
BOUNDARY_MAP1 = [
    [0, [], []],
    [0, [], []],
    [1, [0, 1], [1, -1]],
    [0, [], []],  # 0-3
    [1, [1, 3], [1, -1]],
    [1, [3, 0], [1, -1]],  # 4-5
    [2, [2, 4, 5], [1, 1, 1]],  # 6
]
LEVELS_1 = [0.0, 0.0, 1.0, 1.2, 1.3, 1.3, 2.1]
SYMBOLS_1 = [str(n) for n in range(7)]


CODE2 = """
# symbol dim time = indices : coefs
autoid: true
autosymbol: false
v0 0 0.0 = :
v1 0 0.0 = :
e0 1 1.0 = 0 1 : 2 -2
"""
BOUNDARY_MAP2 = [[0, [], []], [0, [], []], [1, [0, 1], [2, -2]]]
LEVELS_2 = [0.0, 0.0, 1.0]
SYMBOLS_2 = ["v0", "v1", "e0"]


class TestAbstractFiltrationLoader:
    @pytest.mark.parametrize(
        "text, autoid, autosymbol",
        [
            (CODE1, False, True),
            (CODE2, True, False),
        ],
    )
    def test_load(self, text, autoid, autosymbol):
        loader = AbstractFiltrationLoader(io.StringIO(text))
        loader.load()
        assert loader.autoid == autoid
        assert loader.autosymbol == autosymbol

    @pytest.mark.parametrize(
        "text, save_bm, boundary_map, dim, levels, symbols",
        [
            (CODE1, False, BOUNDARY_MAP1, 2, LEVELS_1, SYMBOLS_1),
            (CODE2, False, BOUNDARY_MAP2, 1, LEVELS_2, SYMBOLS_2),
            (CODE1, True, BOUNDARY_MAP1, 2, LEVELS_1, SYMBOLS_1),
            (CODE2, True, BOUNDARY_MAP2, 1, LEVELS_2, SYMBOLS_2),
        ],
    )
    def test_filtration(self, text, save_bm, boundary_map, dim, levels, symbols):
        loader = AbstractFiltrationLoader(io.StringIO(text))
        loader.load()
        filtration = loader.filtration(save_bm)
        assert filtration.boundary_map == boundary_map
        assert filtration.save_boundary_map == save_bm
        assert filtration.dim == dim
        assert filtration.index_to_level == levels
        assert filtration.index_to_symbol == symbols


class TestAbstractFiltration:
    @pytest.mark.parametrize(
        "boundary_map, dim, pairs",
        [
            (BOUNDARY_MAP1, 2, [(0, 1, 2), (0, 3, 4), (1, 5, 6), (0, 0, None)]),
            (BOUNDARY_MAP2, 1, [(0, 0, None), (0, 1, None), (1, 2, None)]),
        ],
    )
    def test_build_phat_matrix(self, boundary_map, dim, pairs):
        filt = AbstractFiltration(boundary_map, dim, None, None, False)
        matrix = filt.build_phat_matrix()
        matrix.reduce_twist()
        assert matrix.birth_death_pairs() == pairs

    @pytest.mark.parametrize("save_bm", [True, False])
    def test_compute_pdgm(self, save_bm):
        f = io.BytesIO()
        AbstractFiltration(BOUNDARY_MAP2, 1, LEVELS_2, SYMBOLS_2, save_bm).compute_pdgm(f)
        f.seek(0)
        pdgmreader = PDGMReader(f)

        assert pdgmreader.metadata["filtration_type"] == "abstract"
        assert pdgmreader.metadata["dim"] == 1

        assert pdgmreader.load_pd_chunk("pd", 0) == ([], [], [0.0, 0.0])
        assert pdgmreader.load_pd_chunk("pd", 1) == ([], [], [1.0])

        assert pdgmreader.load_pd_chunk("indexed_pd", 0) == ([], [], [0, 1])
        assert pdgmreader.load_pd_chunk("indexed_pd", 1) == ([], [], [2])

        all_pairs0 = pdgmreader.load_simple_chunk("allpairs", 0)
        assert all_pairs0 == [[0, None], [1, None]]
        all_pairs1 = pdgmreader.load_simple_chunk("allpairs", 1)
        assert all_pairs1 == [[2, None]]

        index_to_level = pdgmreader.load_simple_chunk("index_to_level")
        assert index_to_level == [0.0, 0.0, 1.0]

        index_to_symbols = pdgmreader.load_simple_chunk("index_to_symbol")
        assert index_to_symbols == ["v0", "v1", "e0"]

        if save_bm:
            assert pdgmreader.load_boundary_map_chunk() == {
                "chunktype": "boundary_map",
                "type": "abstract",
                "map": BOUNDARY_MAP2,
            }
        else:
            assert pdgmreader.load_boundary_map_chunk() is None
