import math

import numpy as np
import pytest

from homcloud.plot_PD_slice import transform_to_x_axis


class Test_transfrom_to_x_axis:
    @pytest.mark.parametrize(
        "v1, v2, transl_expected, matrix_expected",
        [
            (np.array([0, 0]), np.array([1, 0]), [0, 0], np.eye(2, 2)),
            (
                np.array([1, 1]),
                np.array([1, 3]),
                [1, 1],
                np.array(
                    [
                        [0.5 * math.cos(math.pi / 2), 0.5 * math.sin(math.pi / 2)],
                        [-math.sin(math.pi / 2), math.cos(math.pi / 2)],
                    ]
                ),
            ),
        ],
    )
    def test_case(self, v1, v2, transl_expected, matrix_expected):
        transl, matrix = transform_to_x_axis(v1, v2)
        assert np.allclose(transl, transl_expected)
        assert np.allclose(matrix, matrix_expected)

    def test_case_dot(self):
        vs = np.array([[1.0, 2.83], [1.41, 1.51]])
        transl, matrix = transform_to_x_axis(vs[0, :], vs[1, :])
        assert np.allclose((vs - transl) @ matrix.T, np.array([[0, 0], [1, 0]]))

    def test_case_transform_births_deaths(self):
        transl, matrix = transform_to_x_axis(np.array([2.0, 3.0]), np.array([6.0, 7.0]))
        births = np.array([3.0, 5.0])
        deaths = np.array([6.0, 4.0])
        assert np.allclose(
            np.array([[0.5, 0.5], [math.sqrt(2), -math.sqrt(2)]]),
            np.dot(matrix, np.array([births, deaths]) - transl.reshape(2, 1)),
        )
