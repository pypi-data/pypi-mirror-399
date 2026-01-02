import math

import numpy as np
import pytest

import homcloud.alpha_shape3_ext as alpha_shape3_ext
from tests.helper import (
    simplex_alpha_pair_sortkey as sortkey,
    filter_simplex_alpha_pair_by_dim as filter_by_dim,
    extract_simplices_from_simplex_alpha_pair as extract_simplices,
)


def power_k_sphere(weighted_points):
    p0 = weighted_points[0, 0:3]
    p = weighted_points[1:, 0:3]
    w = weighted_points[:, 3]
    beta = np.linalg.norm(p, axis=1) ** 2 - np.vdot(p0, p0) + w[0] - w[1:]
    P = p - p0
    l = np.linalg.solve(2 * np.dot(P, np.transpose(P)), beta - 2 * np.dot(P, p0))  # noqa: E741
    pl = np.dot(np.transpose(P), l)
    return np.linalg.norm(pl) ** 2 - w[0]


class Test_compute:
    def test_for_invalid_array(self):
        with pytest.raises(ValueError, match="Array must be double for an alpha shape"):
            alpha_shape3_ext.compute(np.array([[1, 2, 3]]), False)
        with pytest.raises(ValueError, match="rray must be 2d for an alpha shape"):
            alpha_shape3_ext.compute(np.array([1.0, 2.0, 3.0]), False)
        with pytest.raises(ValueError, match="Incorrect Array shape for an alpha shape"):
            alpha_shape3_ext.compute(np.array([[1.0, 2.0, 3.0, 4.0]]), False)
        with pytest.raises(ValueError, match="Incorrect Array shape for an alpha shape"):
            alpha_shape3_ext.compute(np.array([[1.0, 2.0, 3.0]]), True)

    def test_for_tetrahedron(self, tetrahedron):
        ret = sorted(alpha_shape3_ext.compute(tetrahedron, False), key=sortkey)
        assert ret == [
            ((0,), 0.0),
            ((1,), 0.0),
            ((2,), 0.0),
            ((3,), 0.0),
            ((0, 1), 4**2),
            ((0, 2), 2.5**2 + 3.0**2),
            ((0, 3), 2**2 + 1**2 + 3**2),
            ((1, 2), 1.5**2 + 3**2),
            ((1, 3), 2**2 + 1**2 + 3**2),
            ((2, 3), 0.5**2 + 2**2 + 3**2),
            ((0, 1, 2), 19.0625),
            ((0, 1, 3), pytest.approx(19.6)),
            ((0, 2, 3), pytest.approx(18.922240)),
            ((1, 2, 3), pytest.approx(17.175925)),
            ((0, 1, 2, 3), pytest.approx(21.06944444444444)),
        ]

    def test_case_trigonal_dipyramid(self, trigonal_dipyramid):
        ret = sorted(alpha_shape3_ext.compute(trigonal_dipyramid, False), key=sortkey)
        assert filter_by_dim(ret, 0) == [
            ((0,), 0.0),
            ((1,), 0.0),
            ((2,), 0.0),
            ((3,), 0.0),
            ((4,), 0.0),
        ]
        assert extract_simplices(filter_by_dim(ret, 1)) == [
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 2),
            (1, 3),
            (1, 4),
            (2, 3),
            (2, 4),
        ]
        assert extract_simplices(filter_by_dim(ret, 2)) == [
            (0, 1, 2),
            (0, 1, 3),
            (0, 1, 4),
            (0, 2, 3),
            (0, 2, 4),
            (1, 2, 3),
            (1, 2, 4),
        ]
        assert len(filter_by_dim(ret, 2)) == 7
        assert filter_by_dim(ret, 3) == [
            ((0, 1, 2, 3), pytest.approx(21.06944444444444)),
            ((0, 1, 2, 4), pytest.approx(19.70093233371779)),
        ]

    def test_case_ortho_tetrahedron(self):
        pc = np.array(
            [
                [0, 0, 0],
                [1, 0, 0],
                [0.5, math.sqrt(3) / 2, 0],
                [0.5, math.sqrt(3) / 6, math.sqrt(3.0) / 3],
            ]
        )
        ret = sorted(alpha_shape3_ext.compute(pc, False), key=sortkey)

        # 1 / 3 is the square of the circumradius
        r0 = 1 / 3
        # 1 / 3 is the square of the circumradius of a regular triangle, and
        # r1 = 4 / 15 is the square of the circumradius of the three triangles
        r1 = 4.0 / 15.0
        # 1 / 4 is the square of the half of the longer edges
        # r2 = 1 / 6 is the square of the half of the shorter edges
        r2 = 1.0 / 6.0

        assert ret == [
            ((0,), 0.0),
            ((1,), 0.0),
            ((2,), 0.0),
            ((3,), 0.0),
            ((0, 1), pytest.approx(0.25)),
            ((0, 2), pytest.approx(0.25)),
            ((0, 3), pytest.approx(r2)),
            ((1, 2), pytest.approx(0.25)),
            ((1, 3), pytest.approx(r2)),
            ((2, 3), pytest.approx(r2)),
            ((0, 1, 2), pytest.approx(r0)),
            ((0, 1, 3), pytest.approx(r1)),
            ((0, 2, 3), pytest.approx(r1)),
            ((1, 2, 3), pytest.approx(r1)),
            ((0, 1, 2, 3), pytest.approx(r0)),
        ]

    def test_case_obcute_tetrahedron(self):
        pc = np.array(
            [
                [0, 0, 0],
                [1, 0, 0],
                [0.5, math.sqrt(3) / 2, 0],
                [0.5, math.sqrt(3) / 6, math.sqrt(3.0) / 4],
            ]
        )
        ret = sorted(alpha_shape3_ext.compute(pc, False), key=sortkey)

        # r0 is the square of the circumradius of the tetrahedron
        r0 = (49.0 + 24**2) / (3 * 24**2)
        # r1 is the square of the circumradius of three triangles
        r1 = (25**2 * 12) / (48**2 * 13)
        # r2 is the square of the length of the edge (0, 3)
        r2 = 25 / (48 * 4)

        assert ret == [
            ((0,), 0.0),
            ((1,), 0.0),
            ((2,), 0.0),
            ((3,), 0.0),
            ((0, 1), pytest.approx(0.25)),
            ((0, 2), pytest.approx(0.25)),
            ((0, 3), pytest.approx(r2)),
            ((1, 2), pytest.approx(0.25)),
            ((1, 3), pytest.approx(r2)),
            ((2, 3), pytest.approx(r2)),
            ((0, 1, 2), pytest.approx(r0)),
            ((0, 1, 3), pytest.approx(r1)),
            ((0, 2, 3), pytest.approx(r1)),
            ((1, 2, 3), pytest.approx(r1)),
            ((0, 1, 2, 3), pytest.approx(r0)),
        ]

    def test_for_obcute_obucute_tetrahedron(self):
        pc = np.array(
            [
                [0, 0, 0],
                [1, 0, 0],
                [0.5, math.sqrt(3) / 2, 0],
                [0.5, math.sqrt(3) / 6, math.sqrt(3.0) / 9],
            ]
        )
        ret = sorted(alpha_shape3_ext.compute(pc, False), key=sortkey)

        # r0 is the square of the circumradius
        r0 = 25 / 27
        # r1 is the square of the circumradius of three triangles
        r1 = 10**2 / (27 * 13)
        # r2 is the square of the half of the shorter edges
        r2 = 10 / (27 * 4)

        assert ret == [
            ((0,), 0.0),
            ((1,), 0.0),
            ((2,), 0.0),
            ((3,), 0.0),
            ((0, 1), pytest.approx(r1)),
            ((0, 2), pytest.approx(r1)),
            ((0, 3), pytest.approx(r2)),
            ((1, 2), pytest.approx(r1)),
            ((1, 3), pytest.approx(r2)),
            ((2, 3), pytest.approx(r2)),
            ((0, 1, 2), pytest.approx(r0)),
            ((0, 1, 3), pytest.approx(r1)),
            ((0, 2, 3), pytest.approx(r1)),
            ((1, 2, 3), pytest.approx(r1)),
            ((0, 1, 2, 3), pytest.approx(r0)),
        ]

    def test_case_two_obcute_triangles_tetrahedron(self):
        a = 0.05
        b = 0.1
        pc = np.array(
            [
                [0, 0, 0],
                [1, 0, 0],
                [0.5, a, b],
                [0.5, a, -b],
            ]
        )

        ret = sorted(alpha_shape3_ext.compute(pc, False), key=sortkey)

        r0 = ((a**2 + b**2 - 0.25) / (2 * a)) ** 2 + 0.25
        r1 = (a**2 + b**2 + 0.25) ** 2 / (4 * a**2 + 1)
        e1 = (a**2 + b**2 + 0.25) / 4
        e2 = b**2

        assert ret == [
            ((0,), 0.0),
            ((1,), 0.0),
            ((2,), 0.0),
            ((3,), 0.0),
            ((0, 1), pytest.approx(r0)),
            ((0, 2), pytest.approx(e1)),
            ((0, 3), pytest.approx(e1)),
            ((1, 2), pytest.approx(e1)),
            ((1, 3), pytest.approx(e1)),
            ((2, 3), pytest.approx(e2)),
            ((0, 1, 2), pytest.approx(r0)),
            ((0, 1, 3), pytest.approx(r0)),
            ((0, 2, 3), pytest.approx(r1)),
            ((1, 2, 3), pytest.approx(r1)),
            ((0, 1, 2, 3), pytest.approx(r0)),
        ]

    def test_case_weighted_tetrahedron(self):
        w0 = 0.01
        w1 = 0.3
        w2 = 0.39
        w3 = 0.21
        pc = np.array(
            [
                [-0.12, -0.23, -0.19, w0],
                [1, 0, 0, w1],
                [0, 1, 0, w2],
                [0, 0, 1, w3],
            ]
        )
        ret = sorted(alpha_shape3_ext.compute(pc, True), key=sortkey)

        assert ret == [
            ((0,), -w0),
            ((1,), -w1),
            ((2,), -w2),
            ((3,), -w3),
            ((0, 1), pytest.approx(power_k_sphere(pc[[0, 1], :]))),
            ((0, 2), pytest.approx(power_k_sphere(pc[[0, 2], :]))),
            ((0, 3), pytest.approx(power_k_sphere(pc[[0, 3], :]))),
            ((1, 2), pytest.approx(power_k_sphere(pc[[1, 2], :]))),
            ((1, 3), pytest.approx(power_k_sphere(pc[[1, 3], :]))),
            ((2, 3), pytest.approx(power_k_sphere(pc[[2, 3], :]))),
            ((0, 1, 2), pytest.approx(power_k_sphere(pc[[0, 1, 2], :]))),
            ((0, 1, 3), pytest.approx(power_k_sphere(pc[[0, 1, 3], :]))),
            ((0, 2, 3), pytest.approx(power_k_sphere(pc[[0, 2, 3], :]))),
            ((1, 2, 3), pytest.approx(power_k_sphere(pc[[1, 2, 3], :]))),
            ((0, 1, 2, 3), pytest.approx(power_k_sphere(pc))),
        ]

    def test_case_weighted_obcute_tetrahedron(self):
        w0 = 0.3
        w1 = 0.12
        w2 = 0.09
        w3 = 0.2
        pc = np.array(
            [
                [0, 0, 0, w0],
                [1, 0, 0, w1],
                [0, 1, 0, w2],
                [0, 0, 1, w3],
            ]
        )
        ret = sorted(alpha_shape3_ext.compute(pc, True), key=sortkey)

        assert ret == [
            ((0,), -w0),
            ((1,), -w1),
            ((2,), -w2),
            ((3,), -w3),
            ((0, 1), pytest.approx(power_k_sphere(pc[[0, 1], :]))),
            ((0, 2), pytest.approx(power_k_sphere(pc[[0, 2], :]))),
            ((0, 3), pytest.approx(power_k_sphere(pc[[0, 3], :]))),
            ((1, 2), pytest.approx(power_k_sphere(pc[[0, 1, 2], :]))),
            ((1, 3), pytest.approx(power_k_sphere(pc[[0, 1, 3], :]))),
            ((2, 3), pytest.approx(power_k_sphere(pc[[0, 2, 3], :]))),
            ((0, 1, 2), pytest.approx(power_k_sphere(pc[[0, 1, 2], :]))),
            ((0, 1, 3), pytest.approx(power_k_sphere(pc[[0, 1, 3], :]))),
            ((0, 2, 3), pytest.approx(power_k_sphere(pc[[0, 2, 3], :]))),
            ((1, 2, 3), pytest.approx(power_k_sphere(pc))),
            ((0, 1, 2, 3), pytest.approx(power_k_sphere(pc))),
        ]
