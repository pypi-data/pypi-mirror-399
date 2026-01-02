import numpy as np
import pytest

import homcloud.periodic_alpha_shape3_ext as periodic_alpha_shape3_ext
from tests.helper import simplex_alpha_pair_sortkey as sortkey, filter_simplex_alpha_pair_by_dim as filter_by_dim
import homcloud.cgal_info as cgal_info


class Test_compute:
    def test_case_5x5x5_lattice(self, lattice_5x5x5):
        ret = sorted(periodic_alpha_shape3_ext.compute(lattice_5x5x5, False, *([-0.5, 4.5] * 3)), key=sortkey)

        assert filter_by_dim(ret, 0) == [((i,), 0) for i in range(125)]
        assert 5 * 5 * 5 * 7 == len(filter_by_dim(ret, 1))
        for facet, a in filter_by_dim(ret, 1):
            assert a in [0.25, 0.5, 0.75]
        assert 5 * 5 * 5 * (6 * 4 - 6 - 6) == len(filter_by_dim(ret, 2))
        for facet, a in filter_by_dim(ret, 2):
            assert a in [0.5, 0.75]
        assert 5 * 5 * 5 * 6 == len(filter_by_dim(ret, 3))
        assert np.array([a for (s, a) in ret if len(s) == 3 + 1]) == pytest.approx(0.75)

    def test_case_5x5x5_lattice_with_noise(self, lattice_5x5x5):
        lattice_5x5x5 += np.random.uniform(-1e-10, 1e-10, size=lattice_5x5x5.shape)
        ret = sorted(periodic_alpha_shape3_ext.compute(lattice_5x5x5, False, *([-0.5, 4.5] * 3)), key=sortkey)

        assert filter_by_dim(ret, 0) == [((i,), 0) for i in range(125)]
        assert 5 * 5 * 5 * 7 <= len(filter_by_dim(ret, 1)) <= 5 * 5 * 5 * 9
        assert 5 * 5 * 5 * 12 <= len(filter_by_dim(ret, 2)) <= 5 * 5 * 5 * 15
        assert 5 * 5 * 5 * 6 <= len(filter_by_dim(ret, 3)) <= 5 * 5 * 5 * 8

    @pytest.mark.skipif(cgal_info.numerical_version < 1050601000, reason="CGAL version < 5.6")
    def test_case_5x4x5_lattice_with_noncubic_unit_cell(self):
        lattice_5x4x5 = np.array([(x, y, z) for z in range(5) for y in range(4) for x in range(5)], dtype=float)
        lattice_5x4x5 += np.random.uniform(-0.00001, 0.00001, size=(5 * 4 * 5, 3))
        ret = periodic_alpha_shape3_ext.compute(lattice_5x4x5, False, -0.5, 4.5, -0.5, 3.5, -0.5, 4.5)
        assert sorted(filter_by_dim(ret, 0)) == [((i,), 0) for i in range(100)]
