from unittest.mock import MagicMock

import pytest
import pulp

import homcloud.optvol as optvol


# Tetragon 1
#     4
#  0 --- 1
#  |(9)  |
# 7|  /8 |5
#  | (10)|
#  3 --- 2
#     6
MAP1 = {
    "type": "simplicial",
    "map": [
        [0, []],
        [0, []],
        [0, []],
        [0, []],  # 0, 1, 2, 3
        [1, [1, 0]],
        [1, [2, 1]],
        [1, [3, 2]],  # 4, 5, 6
        [1, [3, 0]],
        [1, [3, 1]],  # 7, 8
        [2, [8, 7, 4]],
        [2, [6, 8, 5]],  # 9, 10
    ],
}

# Tetragon 2
#     4
#  0 --- 1
#  |(10) |
# 9|  /7 |5
#  |  (8)|
#  3 --- 2
#     6
MAP2 = {
    "type": "simplicial",
    "map": [
        [0, []],
        [0, []],
        [0, []],
        [0, []],  # 0, 1, 2, 3
        [1, [1, 0]],
        [1, [2, 1]],
        [1, [3, 2]],  # 4, 5, 6
        [1, [3, 1]],
        [2, [6, 7, 5]],  # 7, 8
        [1, [3, 0]],
        [2, [7, 9, 4]],  # 9, 10
    ],
}


class TestOptimizer:
    @pytest.mark.parametrize(
        "boundary_map, birth, death, active_cells, expected",
        [
            (
                MAP1,
                7,
                10,
                [9, 10],
                (
                    [9, 10],
                    {
                        7: [(-1, 9)],
                        8: [(1, 9), (-1, 10)],
                    },
                ),
            ),
            (MAP2, 9, 10, [10], ([10], {9: [(-1, 10)]})),
            (MAP1, 7, 10, [10], ([10], {7: [], 8: [(-1, 10)]})),
        ],
    )
    def test_build_partial_boundary_matrix(self, boundary_map, birth, death, active_cells, expected):
        def is_active_cell(i):
            return i in active_cells

        optimizer = optvol.Optimizer(birth, death, boundary_map, None)
        assert optimizer.build_partial_boundary_matrix(is_active_cell) == expected

    @pytest.mark.parametrize(
        "birth, death, lpvars, partial_map",
        [
            (7, 10, [9, 10], {7: [(-1, 9)], 8: [(1, 9), (-1, 10)]}),
            (7, 10, [10], {7: [], 8: [(-1, 10)]}),
        ],
    )
    def test_build_lp_problem(self, birth, death, lpvars, partial_map):
        optimizer = optvol.Optimizer(birth, death, None, None)
        optimizer.build_lp_problem(lpvars, partial_map)

    @pytest.mark.parametrize(
        "boundary_map, birth, death, active_cells, result_class, expected_volume",
        [
            (MAP1, 7, 10, [9, 10], optvol.Success, [9, 10]),
            (MAP2, 9, 10, [10], optvol.Success, [10]),
            (MAP1, 7, 10, [10], optvol.Failure, None),
        ],
    )
    def test_find(self, boundary_map, birth, death, active_cells, result_class, expected_volume):
        optimizer = optvol.Optimizer(birth, death, boundary_map, optvol.default_lp_solver())
        result = optimizer.find(lambda i: i in active_cells)
        assert isinstance(result, result_class)
        if isinstance(result, optvol.Success):
            assert result.cell_indices == expected_volume
        else:
            assert result.infeasible


class TestOptimalVolumeFinder:
    def test_to_query_dict(self):
        ovfinder = optvol.OptimalVolumeFinder(
            optvol.RetryOptimizerBuilder(1, None, optvol.default_lp_solver(), None, 0.5, 4)
        )
        wildcard = MagicMock()
        wildcard.__eq__.return_value = True

        d = ovfinder.to_query_dict()
        assert set(d.keys()) == set(
            ["degree", "query-target", "cutoff-radius", "num-retry", "solver-name", "solver-options"]
        )
        assert d["degree"] == 1
        assert d["query-target"] == "optimal-volume"
        assert d["cutoff-radius"] == 0.5
        assert d["num-retry"] == 4


class TestTightenedSubVolumeFinder:
    @pytest.mark.parametrize(
        "epsilon, expected",
        [
            (0.1, [9, 10]),
            (1.1, [10]),
        ],
    )
    def test_find(self, epsilon, expected):
        tsvfinder = optvol.TightenedSubVolumeFinder(
            optvol.OptimizerBuilder(1, MAP1, optvol.default_lp_solver()),
            [0, 0, 0, 0, 0, 0, 0, 1.0, 2.0, 3.0, 4.0],
            epsilon,
        )
        result = tsvfinder.find(7, 10, [9, 10])
        assert result.cell_indices == expected


class TestOptimalVolumeTightenedSubVolumeFinder:
    @pytest.mark.parametrize(
        "epsilon, expected",
        [
            (0.1, [9, 10]),
            (1.1, [10]),
        ],
    )
    def test_find(self, epsilon, expected):
        optimizer_builder = optvol.OptimizerBuilder(1, MAP1, optvol.default_lp_solver())
        tsvfinder = optvol.OptimalVolumeTightenedSubVolumeFinder(
            optimizer_builder, [0, 0, 0, 0, 0, 0, 0, 1.0, 2.0, 3.0, 4.0], epsilon
        )
        result = tsvfinder.find(7, 10)
        assert result.cell_indices == [9, 10]
        assert result.subvolume.cell_indices == expected


def test_find_lp_solver():
    assert type(optvol.find_lp_solver(pulp.getSolver("CPLEX_CMD"), None)) == pulp.CPLEX_CMD
    assert type(optvol.find_lp_solver("coin", {})) == pulp.COIN_CMD
    assert type(optvol.find_lp_solver(None, None)) is type(pulp.LpSolverDefault)
    with pytest.raises(RuntimeError, match="The solver UNKNOWNSOLVER does not exist in PuLP."):
        optvol.find_lp_solver("UNKNOWNSOLVER", {})

    assert type(optvol.find_lp_solver("COIN_CMD", {})) == pulp.COIN_CMD
