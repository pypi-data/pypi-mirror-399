import argparse
import json

from homcloud.version import __version__
from homcloud.argparse_common import parse_range
from homcloud.pdgm_format import PDGMReader
from homcloud.pdgm import PDGM
from homcloud.spatial_searcher import SpatialSearcher
from homcloud.phtrees import PHTrees


class Query:
    def __init__(self, query, volume_getter, searcher, input_dim=None, query_ancestors=False, query_children=False):
        self.query = query
        self.volume_getter = volume_getter
        self.searcher = searcher
        self.input_dim = input_dim
        self.query_ancestors = query_ancestors
        self.query_children = query_children
        self.result = []

    @property
    def degree(self):
        return self.phtrees.degree

    def to_dict(self):
        return {
            "format-version": 2,
            "query": {
                "query-type": "signle",
                "query-target": self.volume_getter.query_target_name,
                "degree": self.input_dim - 1,
                "birth": self.query[0],
                "death": self.query[1],
                "ancestor-pairs": self.query_ancestors,
                "query-children": self.query_children,
            },
            "dimension": self.input_dim,
            "result": [r.to_dict() for r in self.result],
        }


class PointQuery(Query):
    def invoke(self):
        death_index = self.searcher.nearest_pair(*self.query)
        self.result = [self.volume_getter(death_index)]


class RectangleQuery(Query):
    def invoke(self):
        death_indices = self.searcher.in_rectangle(
            self.query[0][0], self.query[0][1], self.query[1][0], self.query[1][1]
        )
        self.result = [self.volume_getter(i) for i in death_indices]


class GetOptimalVolume:
    def __init__(self, phtrees):
        self.phtrees = phtrees

    def __call__(self, death_index):
        return self.phtrees.nodes[death_index]

    query_target_name = "optimal-volume"


class GetStableVolume:
    def __init__(self, phtrees, epsilon):
        self.phtrees = phtrees
        self.epsilon = epsilon

    def __call__(self, death_index):
        return self.phtrees.nodes[death_index].stable_volume(self.epsilon)

    query_target_name = "stable-volume"


def main(args=None):
    if not args:
        args = argument_parser().parse_args()

    with PDGMReader.open(args.input) as reader:
        assert reader.metadata["filtration_type"] in ["alpha", "alpha-phtrees"]
        input_dim = reader.metadata["dim"]
        pdgm = PDGM(reader, input_dim - 1)
        spatial_searcher = SpatialSearcher(pdgm.death_indices, pdgm.births, pdgm.deaths)
        phtrees = PHTrees.from_pdgm(pdgm)

        if is_point_query(args):
            query_class = PointQuery
            query_xy = (args.x, args.y)
        elif is_rectangle_query(args):
            query_class = RectangleQuery
            query_xy = (args.x_range, args.y_range)

        if args.stable_volume:
            volume_getter = GetStableVolume(phtrees, args.stable_volume)
        else:
            volume_getter = GetOptimalVolume(phtrees)

        query = query_class(query_xy, volume_getter, spatial_searcher, input_dim)

        query.invoke()

        if args.json_output:
            with open(args.json_output, "w") as f:
                json.dump(query.to_dict(), f)


def is_point_query(args):
    return args.x is not None and args.y is not None


def is_rectangle_query(args):
    return args.x_range is not None and args.y_range is not None


def argument_parser():
    p = argparse.ArgumentParser(description="")
    p.add_argument("-V", "--version", action="version", version=__version__)
    p.add_argument("-x", type=float, help="birth time of the pair")
    p.add_argument("-y", type=float, help="death time of the pair")
    p.add_argument("-X", "--x-range", type=parse_range, help="birth time of the pair")
    p.add_argument("-Y", "--y-range", type=parse_range, help="death time of the pair")
    p.add_argument("-j", "--json-output", help="output in json format")
    p.add_argument("-S", "--stable-volume", type=float, help="stable volume epsilon")
    p.add_argument("input", help="input pht file")
    return p


if __name__ == "__main__":
    main()
