import numpy as np
import pytest

import homcloud.alpha_shape2_ext as alpha_shape2_ext
from tests.helper import (
    simplex_alpha_pair_sortkey as sortkey,
    extract_simplices_from_simplex_alpha_pair as extract_simplices,
    minimal_squared_circumradius,
)


class Test_compute:
    def test_case_tetragon(self, tetragon):
        ret = sorted(alpha_shape2_ext.compute(tetragon, False), key=sortkey)
        assert ret == [
            ((0,), 0),
            ((1,), 0),
            ((2,), 0),
            ((3,), 0),
            ((0, 1), 8.5),
            ((0, 2), 9.0),
            ((0, 3), 5.0),
            ((1, 2), 8.5),
            ((2, 3), 8.0),
            ((0, 1, 2), pytest.approx(minimal_squared_circumradius(tetragon[[0, 1, 2], :]))),
            ((0, 2, 3), pytest.approx(minimal_squared_circumradius(tetragon[[0, 2, 3], :]))),
        ]

    def test_case_obcute_triangle(self, obtuse_triangle):
        ret = sorted(alpha_shape2_ext.compute(obtuse_triangle, False), key=sortkey)
        a = minimal_squared_circumradius(obtuse_triangle)
        assert ret == [
            ((0,), 0.0),
            ((1,), 0.0),
            ((2,), 0.0),
            ((0, 1), pytest.approx(a)),
            ((0, 2), 0.1**2 + 0.05**2),
            ((1, 2), 0.4**2 + 0.05**2),
            ((0, 1, 2), pytest.approx(a)),
        ]

    def test_case_weighted_tetragon(self, tetragon_weighted):
        ret = sorted(alpha_shape2_ext.compute(tetragon_weighted, True), key=sortkey)
        assert ret[:4] == [
            ((0,), -1.0),
            ((1,), -4.0),
            ((2,), 0),
            ((3,), -1.0),
        ]
        assert extract_simplices(ret[4:9]) == [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]
        assert np.all(np.array([a for (_, a) in ret[4:9]]) < [8.5, 9.0, 5.0, 8.5, 8.0])
        assert extract_simplices(ret[9:]) == [(0, 1, 2), (0, 2, 3)]
        assert np.all(np.array([a for (_, a) in ret[9:]]) < [11.4, 10])

    def test_case_shape_mismatch(self):
        with pytest.raises(ValueError, match="Incorrect Array shape for an alpha shape"):
            alpha_shape2_ext.compute(np.array([[1.0, 2.0, 1.0], [3.0, 4.0, 2.0], [10.0, -1.0, 2.0]]), False)

    def test_case_shape_mismatch_with_weight(self):
        with pytest.raises(ValueError, match="Incorrect Array shape for an alpha shape"):
            alpha_shape2_ext.compute(np.array([[1.0, 2.0, 1.0, 0.0], [3.0, 4.0, 2.0, 0.0]]), True)

    def test_case_type_mismatch(self):
        with pytest.raises(ValueError, match="Array must be double for an alpha shape"):
            alpha_shape2_ext.compute(np.array([[True, True], [True, False], [False, False]]), False)
