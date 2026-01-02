from cached_property import cached_property
import numpy as np


class Volume:
    def birth_simplex(self, by="coordinates"):
        return self.get_geometry_resolver(by).resolve_cell(self.birth_index)

    def death_simplex(self, by="coordinates"):
        return self.get_geometry_resolver(by).resolve_cell(self.death_index)

    def boundary(self, by="coordinates"):
        return self.get_geometry_resolver(by).resolve_boundary(self.volume_indices())

    def boundary_vertices(self, by="coordinates"):
        return self.get_geometry_resolver(by).resolve_boundary_vertices(self.volume_indices())

    def vertices(self, by="coordinates"):
        return self.get_geometry_resolver(by).resolve_vertices(self.volume_indices())

    def simplices(self, by="coordinates"):
        return self.get_geometry_resolver(by).resolve_cells(self.volume_indices())

    def volume_indices(self):
        return (n.death_index for n in self.volume_nodes)

    def to_dict(self):
        return {
            "birth-index": self.birth_index,
            "death-index": self.death_index,
            "birth-time": self.birth_time(),
            "death-time": self.death_time(),
            "boundary": self.boundary(),
            "boundary-by-symbols": self.boundary("symbols"),
            "boundary-vertices": self.boundary_vertices(),
            "boundary-vertices-by-symbols": self.boundary_vertices("symbols"),
            "vertices": self.vertices(),
            "vertices-by-symbols": self.vertices("symbols"),
            "simplices": self.simplices(),
            "simplices-by-symbols": self.simplices("symbols"),
            "children": self.children_dicts(),
        }

    def to_child_dict(self):
        return {
            "birth-index": self.birth_index,
            "death-index": self.death_index,
            "birth-time": self.birth_time(),
            "death-time": self.death_time(),
            "children": self.children_dicts(),
        }

    def children_dicts(self):
        return [child.to_child_dict() for child in self.children]

    def __repr__(self):
        return "{}.{}(birth_time={}, death_time={})".format(
            self.__class__.__module__, self.__class__.__name__, self.birth_time(), self.death_time()
        )


class Node(Volume):
    def __init__(self, birth_index, death_index, parent_death, trees=None):
        self.birth_index = birth_index
        self.death_index = death_index
        self.parent_death = parent_death
        self.trees = trees
        self.volume_cache = None
        self.children = []

    def isroot(self):
        return self.parent_death == np.inf

    def birth_time(self):
        return self.trees.index_to_level[self.birth_index]

    def death_time(self):
        return self.trees.index_to_level[self.death_index]

    def lifetime(self):
        return self.death_time() - self.birth_time()

    @cached_property
    def volume_nodes(self):
        volume_nodes = []

        def iter(n):
            volume_nodes.append(n)
            for child in n.children:
                iter(child)

        iter(self)
        return volume_nodes

    def volume_size(self):
        return len(self.volume_nodes)

    def stable_volume(self, epsilon, cls=None):
        cls = cls or StableVolume
        return cls(self, [child for child in self.children if child.birth_time() > self.birth_time() + epsilon])

    def get_geometry_resolver(self, by="coordinates"):
        return self.trees.get_geometry_resolver(by)


class StableVolume(Volume):
    def __init__(self, root, children):
        self.root = root
        self.children = children
        self.volume_cache = None

    @property
    def trees(self):
        return self.root.trees

    @property
    def birth_index(self):
        return self.root.birth_index

    @property
    def death_index(self):
        return self.root.death_index

    def birth_time(self):
        return self.root.birth_time()

    def death_time(self):
        return self.root.death_time()

    def lifetime(self):
        return self.death_time() - self.birth_time()

    def get_geometry_resolver(self, by="coordinates"):
        return self.root.get_geometry_resolver(by)

    @cached_property
    def volume_nodes(self):
        volume_nodes = [self.root]
        for child in self.children:
            volume_nodes.extend(child.volume_nodes)
        return volume_nodes


class PHTrees:
    def __init__(self, nodes, index_to_level=None, coord_resolver=None, symbol_resolver=None, nodeclass=Node):
        assert nodes is not None
        self.nodes = {
            death_index: nodeclass(birth_index, death_index, parent_death, self)
            for (birth_index, death_index, parent_death) in nodes
        }
        self.index_to_level = index_to_level
        self.coord_resolver = coord_resolver
        self.symbol_resolver = symbol_resolver
        self.roots = []
        self.build_tree()

    @staticmethod
    def from_pdgmreader(reader):
        return PHTrees(
            reader.load_simple_chunk("phtrees"),
            reader.load_simple_chunk("index_to_level"),
        )

    @staticmethod
    def from_pdgm(pdgm, nodeclass=Node):
        return PHTrees(
            pdgm.pdgmreader.load_simple_chunk("phtrees"),
            pdgm.index_to_level,
            pdgm.get_geometry_resolver("coordinates"),
            pdgm.get_geometry_resolver("symbols"),
            nodeclass,
        )

    def build_tree(self):
        for node in self.nodes.values():
            if node.isroot():
                self.roots.append(node)
            else:
                self.nodes[node.parent_death].children.append(node)

    def parent_of(self, node):
        if node.isroot():
            return None
        return self.nodes[node.parent_death]

    def get_geometry_resolver(self, type):
        if type == "coordinates":
            return self.coord_resolver
        if type == "symbols":
            return self.symbol_resolver
        raise ValueError("Unknown type: {}".format(type))
