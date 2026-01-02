import numpy as np
import pytest

import homcloud.periodic_alpha_shape2_ext as periodic_alpha_shape2_ext
from tests.helper import (
    simplex_alpha_pair_sortkey as sortkey,
    filter_simplex_alpha_pair_by_dim as filter_by_dim,
    extract_simplices_from_simplex_alpha_pair as extract_simplices,
)


@pytest.fixture
def pc_3x3():
    pc = np.array([[x + 0.5, y + 0.5] for x in range(3) for y in range(3)])
    pc += np.random.uniform(-1e-10, 1e-10, size=pc.shape)
    return pc


class Test_compute:
    def test_case_3x3(self, pc_3x3):
        ret = sorted(periodic_alpha_shape2_ext.compute(pc_3x3, False, 0.0, 3.0, 0.0, 3.0), key=sortkey)

        assert len(ret) == 9 + 27 + 18

        for i, (simplex, a) in enumerate(ret[:9]):
            assert simplex == (i,)
            assert a == 0.0

        for simplex, a in ret[9 : 9 + 27]:
            assert len(simplex) == 2
            assert a in [pytest.approx(0.25), pytest.approx(0.5)]

        edges = set(extract_simplices(filter_by_dim(ret, 1)))
        expected_horizontal_edges = set([(0, 3), (1, 4), (2, 5), (3, 6), (4, 7), (5, 8), (0, 6), (1, 7), (2, 8)])
        assert expected_horizontal_edges.issubset(edges)
        expected_vertical_edges = set([(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (6, 7), (7, 8), (6, 8)])
        assert expected_vertical_edges.issubset(edges)

        for simplex, a in ret[9 + 27 :]:
            assert len(simplex) == 3
            assert a == pytest.approx(0.5)

    def test_case_weighted(self):
        with pytest.raises(ValueError, match="2D Periodic alpha shape does not accept weighted points"):
            periodic_alpha_shape2_ext.compute(np.array([[0.0, 0, 0], [0, 1, 0], [1, 0, 0]]), True, 0, 2, 0, 2)

    def test_case_too_anistropic_domain(self, pc_3x3):
        with pytest.raises(ValueError, match="Too anistropic periodic region is invalid"):
            periodic_alpha_shape2_ext.compute(pc_3x3, False, 0, 1, 0, 2)

    def test_case_invalid_domain(self, pc_3x3):
        with pytest.raises(ValueError, match="Periodic region invalid"):
            periodic_alpha_shape2_ext.compute(pc_3x3, False, 0, 0, 3, 3)

    def test_case_2x2(self):
        pc = np.array([[0.49, 0.49], [0.5, 1.5], [1.5, 0.5], [1.51, 1.51]])
        with pytest.raises(
            ValueError, match="Points are too few for periodic 2D alpha shape. 1-sheet covering is not allowed"
        ):
            periodic_alpha_shape2_ext.compute(pc, False, 0.0, 2.0, 0.0, 2.0)

    def test_case_out_of_domain(self, pc_3x3):
        with pytest.raises(ValueError, match="Point out of the unit cell"):
            periodic_alpha_shape2_ext.compute(pc_3x3, False, 0.0, 2.0, 0.0, 3.0)
