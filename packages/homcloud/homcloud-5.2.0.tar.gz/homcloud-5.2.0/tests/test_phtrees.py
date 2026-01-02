import numpy as np
import pytest

import homcloud.phtrees as phtrees
import homcloud.geometry_resolver as geom_resolver


NODES1 = [[8, 9, 10], [7, 10, np.inf]]
INDEX_TO_LEVEL = {7: 1.0, 8: 2.0, 9: 2.0, 10: 3.0}
INDEX_TO_SIMPLEX = {
    4: [0, 1],
    5: [1, 2],
    6: [2, 3],
    7: [0, 3],
    8: [1, 3],
    9: [0, 1, 3],
    10: [1, 2, 3],
}
VERTEX_SYMBOLS = ["X", "Y", "Z", "U"]
VERTEX_COORDINATES = [[0, 0], [1, 0.5], [2, 0], [1, -0.5]]


@pytest.fixture
def trees1():
    def boundary_map(index):
        if index == 9:
            return [4, 7, 8]
        if index == 10:
            return [5, 6, 8]

    coord_resolver = geom_resolver.SimplicialResolver(INDEX_TO_SIMPLEX, VERTEX_COORDINATES, boundary_map)
    symbol_resolver = geom_resolver.SimplicialResolver(INDEX_TO_SIMPLEX, VERTEX_SYMBOLS, boundary_map)

    return phtrees.PHTrees(NODES1, INDEX_TO_LEVEL, coord_resolver, symbol_resolver)


class TestPHTrees:
    class Test_nodes:
        def test_case_MAP1(self):
            trees = phtrees.PHTrees(NODES1)
            assert len(trees.nodes) == 2
            trees.nodes[9].birth_index == 8
            trees.nodes[9].death_index == 9
            trees.nodes[9].parent_death == 10

    def test_parent_of(self):
        trees = phtrees.PHTrees(NODES1)
        parent = trees.parent_of(trees.nodes[9])
        assert parent.birth_index == 7
        assert trees.parent_of(parent) is None


class TestNode:
    @pytest.fixture
    def node(self, trees1):
        return phtrees.Node(7, 10, np.inf, trees1)

    def test_birth_time(self, node):
        assert node.birth_time() == 1.0

    def test_death_time(self, node):
        assert node.death_time() == 3.0

    def test_lifetime(self, node):
        assert node.lifetime() == 2.0

    def test_birth_simplex(self, node):
        assert sorted(node.birth_simplex()) == sorted([[0, 0], [1, -0.5]])

    def test_death_simplex(self, node):
        assert sorted(node.death_simplex()) == sorted([[1, 0.5], [2, 0], [1, -0.5]])

    def test_birth_simplex_by_symbols(self, node):
        assert sorted(node.birth_simplex("symbols")) == sorted(["X", "U"])

    def test_death_simplex_by_symbols(self, node):
        assert sorted(node.death_simplex("symbols")) == sorted(["Y", "Z", "U"])

    def test_volume_nodes(self, trees1):
        assert trees1.nodes[9].volume_nodes == [trees1.nodes[9]]
        assert trees1.nodes[10].volume_nodes == [trees1.nodes[10], trees1.nodes[9]]

    def test_boundary(self, trees1):
        assert sorted(trees1.nodes[10].boundary("symbols")) == sorted([["X", "Y"], ["Y", "Z"], ["Z", "U"], ["X", "U"]])

    def test_boundary_vertices(self, trees1):
        node = trees1.nodes[10]
        assert sorted(node.boundary_vertices("symbols")) == sorted(
            [
                "X",
                "Y",
                "Z",
                "U",
            ]
        )

    def test_vertices(self, trees1):
        node = trees1.nodes[10]
        assert sorted(node.vertices("symbols")) == sorted(
            [
                "X",
                "Y",
                "Z",
                "U",
            ]
        )

    def test_simplices(self, trees1):
        node = trees1.nodes[10]
        assert sorted(node.simplices("symbols")) == sorted(
            [
                ["X", "Y", "U"],
                ["Y", "Z", "U"],
            ]
        )

    def test_stable_volume(self, trees1):
        node = trees1.nodes[10]
        assert isinstance(node.stable_volume(0.1), phtrees.StableVolume)
        assert node.stable_volume(0.1).volume_nodes == [trees1.nodes[10], trees1.nodes[9]]
        assert node.stable_volume(1.1).volume_nodes == [trees1.nodes[10]]

    def test_to_dict(self, trees1):
        node = trees1.nodes[10]
        dict = node.to_dict()
        assert sorted(dict.keys()) == sorted(
            [
                "birth-index",
                "death-index",
                "birth-time",
                "death-time",
                "boundary",
                "boundary-by-symbols",
                "boundary-vertices",
                "boundary-vertices-by-symbols",
                "vertices",
                "vertices-by-symbols",
                "simplices",
                "simplices-by-symbols",
                "children",
            ]
        )
        assert dict["birth-index"] == 7
        assert dict["death-index"] == 10
        assert dict["birth-time"] == 1.0
        assert dict["death-time"] == 3.0

        assert sorted(dict["boundary"]) == sorted(
            [[[0, 0], [1, 0.5]], [[1, 0.5], [2, 0]], [[2, 0], [1, -0.5]], [[0, 0], [1, -0.5]]]
        )
        assert sorted(dict["boundary-by-symbols"]) == sorted([["X", "Y"], ["Y", "Z"], ["Z", "U"], ["X", "U"]])

        assert sorted(dict["boundary-vertices"]) == sorted([[0, 0], [1, 0.5], [2, 0], [1, -0.5]])
        assert sorted(dict["boundary-vertices-by-symbols"]) == sorted(
            [
                "X",
                "Y",
                "Z",
                "U",
            ]
        )

        assert sorted(dict["vertices"]) == sorted([[0, 0], [1, 0.5], [2, 0], [1, -0.5]])
        assert sorted(dict["vertices-by-symbols"]) == sorted(
            [
                "X",
                "Y",
                "Z",
                "U",
            ]
        )

        assert sorted(dict["simplices"]) == sorted(
            [
                [[0, 0], [1, 0.5], [1, -0.5]],
                [[1, 0.5], [2, 0], [1, -0.5]],
            ]
        )
        assert sorted(dict["simplices-by-symbols"]) == sorted(
            [
                ["X", "Y", "U"],
                ["Y", "Z", "U"],
            ]
        )

        assert dict["children"] == [
            {
                "birth-index": 8,
                "death-index": 9,
                "birth-time": 2.0,
                "death-time": 2.0,
                "children": [],
            }
        ]
