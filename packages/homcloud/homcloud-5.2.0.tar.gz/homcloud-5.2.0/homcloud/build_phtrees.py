from collections import defaultdict

import numpy as np

from homcloud.pdgm_format import PDGMWriter, SimpleChunk


def coboundary_map(input_dim, boundary_map):
    cobmap = defaultdict(list)
    for index, (d, boundary) in enumerate(boundary_map):
        if d == input_dim:
            for b in boundary:
                cobmap[b].append(index)
    return cobmap


class PHTrees:
    def __init__(self, input_dim, boundary_map):
        self.input_dim = input_dim
        self.coboundary_map = coboundary_map(input_dim, boundary_map)
        self.nodes = dict()
        self.infinity = Node(np.inf)
        self.build()

    def node(self, index):
        if index in self.nodes:
            return self.nodes[index]
        else:
            self.nodes[index] = Node(index)
            return self.nodes[index]

    def root(self, node):
        if node.shortcut is None:
            return node
        root = self.root(node.shortcut)
        node.shortcut = root
        return root

    def build(self):
        def merge(root1, root2):
            if root1.death_index == root2.death_index:
                pass
            elif root1.death_index < root2.death_index:
                root1.birth_index = facet
                root1.parent = root2.death_index
                root1.shortcut = root2
            else:
                root2.birth_index = facet
                root2.parent = root1.death_index
                root2.shortcut = root1

        for facet, coboundary in sorted(self.coboundary_map.items(), reverse=True):
            if len(coboundary) == 2:
                merge(self.root(self.node(coboundary[0])), self.root(self.node(coboundary[1])))
            else:
                merge(self.root(self.node(coboundary[0])), self.infinity)

    def to_list(self):
        return [node.to_list() for node in self.nodes.values()]

    def all_pairs(self):
        return [node.to_pair(self.input_dim) for node in self.nodes.values()]

    def save_pdgm(self, f, filt):
        writer = PDGMWriter(f, "alpha-phtrees", self.input_dim)
        writer.save_pairs(self.all_pairs(), filt.index_to_level)
        writer.append_chunk(filt.alpha_information_chunk())
        writer.append_chunk(SimpleChunk("index_to_level", filt.index_to_level))
        writer.append_chunk(SimpleChunk("vertex_symbols", filt.symbols))
        writer.append_chunk(SimpleChunk("vertex_coordintes", filt.coordinates.tolist()))
        writer.append_chunk(SimpleChunk("index_to_simplex", filt.index_to_simplex))
        writer.append_chunk(SimpleChunk("phtrees", self.to_list()))
        writer.write()


class Node:
    def __init__(self, death_index):
        self.death_index = death_index
        self.birth_index = None
        self.shortcut = None
        self.parent = None

    def to_list(self):
        return [self.birth_index, self.death_index, self.parent]

    def to_pair(self, dim):
        return (dim - 1, self.birth_index, self.death_index)
