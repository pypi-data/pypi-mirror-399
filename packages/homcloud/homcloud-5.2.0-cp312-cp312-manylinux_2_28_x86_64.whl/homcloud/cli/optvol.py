import argparse
from pathlib import Path
import json

import pulp

from homcloud.argparse_common import parse_range, parse_bool
from homcloud.license import add_argument_for_license
from homcloud.version import __version__
from homcloud.pdgm import PDGM
from homcloud.spatial_searcher import SpatialSearcher
from homcloud.numpyencoder import NumpyEncoder
from homcloud.delegate import forwardable
from homcloud.optvol import (
    find_lp_solver,
    OptimizerBuilder,
    OptimalVolumeFinder,
    TightenedVolumeFinder,
    OptimalVolumeTightenedSubVolumeFinder,
)


@forwardable
class Main:
    def __init__(self, args):
        self.args = args

    __delegator_definitions__ = {"args": ["input", "degree", "cutoff_radius", "retry"]}

    def run(self):
        if self.input_is_pdgm:
            with PDGM.open(self.input, self.degree) as pdgm:
                self.setup_pdgm(pdgm)

        ovfinder = self.build_ovfinder()
        query = self.build_query(ovfinder)
        results = query.execute()

        if self.is_json_output:
            self.write_json(query, results)

    @property
    def input_is_pdgm(self):
        return Path(self.input).suffix == ".pdgm"

    @property
    def lp_solver(self):
        return find_lp_solver(self.args.solver, self.args.option)

    @property
    def is_json_output(self):
        return self.args.json_output

    @property
    def points(self):
        return self.coord_resolver.vertices

    def setup_pdgm(self, pdgm):
        if pdgm.filtration_type == "alpha":
            self.setup_alpha_pdgm(pdgm)
        elif pdgm.filtration_type == "abstract":
            self.setup_abstract_pdgm(pdgm)
        elif pdgm.filtration_type == "simplicial":
            self.setup_simplicial_pdgm(pdgm)
        elif pdgm.filtration_type == "cubical":
            self.setup_cubical_pdgm(pdgm)
        else:
            raise RuntimeError("Unknown pdgm type: {}".format(pdgm.filtration_type))
        self.filtration_type = pdgm.filtration_type
        self.spatial_searcher = build_spatial_searcher(pdgm)
        self.index_to_level = pdgm.index_to_level

    def setup_alpha_pdgm(self, pdgm):
        self.optimizer_builder = OptimizerBuilder.from_alpha_pdgm(pdgm, self.cutoff_radius, self.retry, self.lp_solver)
        self.success_to_dict = SuccessToDictAlpha.from_pdgm(pdgm)
        self.coord_resolver = pdgm.alpha_coord_resolver

    def setup_abstract_pdgm(self, pdgm):
        self.optimizer_builder = OptimizerBuilder(self.degree, pdgm.boundary_map_chunk, self.lp_solver)
        self.success_to_dict = SuccessToDictAbstract.from_pdgm(pdgm)

    def setup_simplicial_pdgm(self, pdgm):
        self.optimizer_builder = OptimizerBuilder(self.degree, pdgm.boundary_map_chunk, self.lp_solver)
        self.success_to_dict = SuccessToDictSimplicial.from_pdgm(pdgm)

    def setup_cubical_pdgm(self, pdgm):
        self.optimizer_builder = OptimizerBuilder.from_cubical_pdgm(
            pdgm, self.cutoff_radius, self.retry, self.lp_solver
        )
        self.success_to_dict = SuccessToDictCubical.from_pdgm(pdgm)
        self.cube_resolver = pdgm.cubical_geometry_resolver

    def build_ovfinder(self):
        type = self.args.type
        if type == "optimal-volume":
            return OptimalVolumeFinder(self.optimizer_builder)
        elif type == "tightened-volume":
            return TightenedVolumeFinder(self.optimizer_builder, self.index_to_level, self.args.epsilon)
        elif type == "tightened-subvolume":
            return OptimalVolumeTightenedSubVolumeFinder(
                self.optimizer_builder, self.index_to_level, self.args.epsilon
            )
        else:
            raise RuntimeError("Unknown type: {}".format(type))

    def build_query(self, ovfinder):
        if PointQuery.valid_args(self.args):
            return PointQuery(self.args.x, self.args.y, ovfinder, self.spatial_searcher)
        elif RectangleQuery.valid_args(self.args):
            return RectangleQuery(
                self.args.x_range, self.args.y_range, ovfinder, self.spatial_searcher, self.args.skip_infeasible
            )
        else:
            raise RuntimeError("Invalid query")

    def write_json(self, query, results):
        with open(self.args.json_output, "w") as f:
            json.dump(self.build_jsondict(query, results), f, cls=NumpyEncoder)

    def build_jsondict(self, query, results):
        def result_to_dict(result):
            if result.success:
                return self.success_to_dict(result)
            else:
                return failure_to_dict(result)

        return {"format-version": 2.0, "query": query.to_dict(), "result": [result_to_dict(r) for r in results]}


def failure_to_dict(failure):
    return {
        "birth-time": failure.pair[0],
        "death-time": failure.pair[1],
        "success": False,
        "status": pulp.LpStatus[failure.status],
    }


def main(args=None):
    Main(args or argument_parser().parse_args()).run()


def argument_parser():
    p = argparse.ArgumentParser()
    p.description = "Copmutes optimal volumes and variants of stable volumes"
    p.add_argument("-V", "--version", action="version", version=__version__)
    add_argument_for_license(p)

    tp = p.add_argument_group("target")
    tp.add_argument("-d", "--degree", type=int, required=True, help="degree of PH")
    tp.add_argument("-x", type=float, help="birth time of the pair")
    tp.add_argument("-y", type=float, help="death time of the pair")
    tp.add_argument("-X", "--x-range", type=parse_range, help="birth time of the pair")
    tp.add_argument("-Y", "--y-range", type=parse_range, help="death time of the pair")

    op = p.add_argument_group("output options")
    op.add_argument("-j", "--json-output", help="output in json format")

    cp = p.add_argument_group("computation parameters")
    cp.add_argument(
        "-T",
        "--type",
        default="optimal-volume",
        help="target type (*optimal-volume*, tightened-volume," " or tightened-subvolume",
    )
    cp.add_argument("-e", "--epsilon", type=float, default=0.0, help="tighened-volume/subvolume epsilon")
    cp.add_argument("-c", "--cutoff-radius", type=float, help="cut-off radius in R^n")
    cp.add_argument("-n", "--retry", type=int, default=1, help="number of retry")
    cp.add_argument("--skip-infeasible", default=False, type=parse_bool, help="skip infeasible (on/*off*)")

    sp = p.add_argument_group("solver parameters")
    sp.add_argument("--solver", help="LP solver name")
    sp.add_argument("-O", "--option", action="append", default=[], help="options for LP solver")

    p.add_argument("input", help="input filename")
    return p


def build_spatial_searcher(diagram):
    return SpatialSearcher(
        list(zip(zip(diagram.birth_indices, diagram.death_indices), zip(diagram.births, diagram.deaths))),
        diagram.births,
        diagram.deaths,
    )


class PointQuery:
    def __init__(self, birth_time, death_time, ovfinder, spatial_searcher):
        self.birth_time = birth_time
        self.death_time = death_time
        self.ovfinder = ovfinder
        self.spatial_searcher = spatial_searcher

    def to_dict(self):
        return dict(
            self.ovfinder.to_query_dict(),
            **{
                "birth": self.birth_time,
                "death": self.death_time,
            },
        )

    def execute(self):
        pair_indices, pair = self.spatial_searcher.nearest_pair(self.birth_time, self.death_time)
        result = self.ovfinder.find(*pair_indices)
        result.pair = pair
        return [result]

    @staticmethod
    def valid_args(args):
        return args.x is not None and args.y is not None


class RectangleQuery:
    def __init__(self, birth_range, death_range, ovfinder, spatial_searcher, skip_infeasible):
        self.birth_range = birth_range
        self.death_range = death_range
        self.ovfinder = ovfinder
        self.spatial_searcher = spatial_searcher
        self.skip_infeasible = skip_infeasible

    def to_dict(self):
        return dict(
            self.ovfinder.to_query_dict(),
            **{
                "birth-range": self.birth_range,
                "death-range": self.death_range,
                "skip-infeasible": self.skip_infeasible,
            },
        )

    def pairs_in_rectangle(self):
        return self.spatial_searcher.in_rectangle(
            self.birth_range[0], self.birth_range[1], self.death_range[0], self.death_range[1]
        )

    def execute(self):
        results = []
        for pair_indices, pair in self.pairs_in_rectangle():
            result = self.ovfinder.find(*pair_indices)
            result.pair = pair
            if result.success:
                results.append(result)
            elif result.infeasible and self.skip_infeasible:
                results.append(result)
            else:
                raise RuntimeError(result.message)
        return results

    @staticmethod
    def valid_args(args):
        return args.x_range and args.y_range


class SuccessToDictBase:
    def __init__(self, index_to_level, death_to_birth):
        self.index_to_level = index_to_level
        self.death_to_birth = death_to_birth

    def children(self, death, success):
        ret = []
        for b, d in success.children(death, self.death_to_birth):
            birth_time = self.index_to_level[b]
            death_time = self.index_to_level[d]
            if birth_time == death_time:
                pass
            ret.append(
                {
                    "birth-time": birth_time,
                    "death-time": death_time,
                    "birth-index": b,
                    "death-index": d,
                }
            )

        return ret

    def basedict(self, success, death):
        birth = self.death_to_birth[death]

        return {
            "birth-time": self.index_to_level[birth],
            "death-time": self.index_to_level[death],
            "birth-index": birth,
            "death-index": death,
            "success": True,
            "tightened-subvolume": self(success.subvolume),
        }


class SuccessToDictAlpha(SuccessToDictBase):
    def __init__(self, index_to_level, coord_resolver, symbol_resolver, death_to_birth):
        super().__init__(index_to_level, death_to_birth)
        self.coord_resolver = coord_resolver
        self.symbol_resolver = symbol_resolver

    @staticmethod
    def from_pdgm(pdgm):
        return SuccessToDictAlpha(
            pdgm.index_to_level, pdgm.alpha_coord_resolver, pdgm.alpha_symbol_resolver, pdgm.death_index_to_birth_index
        )

    def __call__(self, success):
        if success is None:
            return None

        death = max(success.cell_indices)

        return dict(
            self.basedict(success, death),
            **{
                "points": self.coord_resolver.resolve_vertices(success.cell_indices),
                "simplices": self.coord_resolver.resolve_cells(success.cell_indices),
                "boundary": self.coord_resolver.resolve_cells(
                    self.coord_resolver.boundary_cells(success.cell_indices)
                ),
                "boundary-points": self.coord_resolver.resolve_vertices(
                    self.coord_resolver.boundary_cells(success.cell_indices)
                ),
                "points-symbols": self.symbol_resolver.resolve_vertices(success.cell_indices),
                "simplices-symbols": self.symbol_resolver.resolve_cells(success.cell_indices),
                "boundary-symbols": self.symbol_resolver.resolve_cells(
                    self.symbol_resolver.boundary_cells(success.cell_indices)
                ),
                "boundary-points-symbols": self.symbol_resolver.resolve_vertices(
                    self.symbol_resolver.boundary_cells(success.cell_indices)
                ),
                "children": self.children(death, success),
            },
        )


class SuccessToDictAbstract(SuccessToDictBase):
    def __init__(self, index_to_level, abs_resolver, death_to_birth):
        super().__init__(index_to_level, death_to_birth)
        self.abs_resolver = abs_resolver

    def __call__(self, success):
        if success is None:
            return None

        death = max(success.cell_indices)
        return dict(
            self.basedict(success, death),
            **{
                "cells": self.abs_resolver.resolve_cells(success.cell_indices),
                "boundary": self.abs_resolver.resolve_cells(self.abs_resolver.boundary_cells(success.cell_indices)),
                "children": self.children(death, success),
            },
        )

    @staticmethod
    def from_pdgm(pdgm):
        return SuccessToDictAbstract(
            pdgm.index_to_level, pdgm.abstract_geometry_resolver, pdgm.death_index_to_birth_index
        )


class SuccessToDictSimplicial(SuccessToDictBase):
    def __init__(self, index_to_level, symbol_resolver, death_to_birth):
        super().__init__(index_to_level, death_to_birth)
        self.symbol_resolver = symbol_resolver

    def __call__(self, success):
        if success is None:
            return None

        death = max(success.cell_indices)
        return dict(
            self.basedict(success, death),
            **{
                "points-symbols": self.symbol_resolver.resolve_vertices(success.cell_indices),
                "simplices-symbols": self.symbol_resolver.resolve_cells(success.cell_indices),
                "boundary-symbols": self.symbol_resolver.resolve_cells(
                    self.symbol_resolver.boundary_cells(success.cell_indices)
                ),
                "boundary-points-symbols": self.symbol_resolver.resolve_vertices(
                    self.symbol_resolver.boundary_cells(success.cell_indices)
                ),
                "children": self.children(death, success),
            },
        )

    @staticmethod
    def from_pdgm(pdgm):
        return SuccessToDictSimplicial(
            pdgm.index_to_level, pdgm.simplicial_symbol_resolver, pdgm.death_index_to_birth_index
        )


class SuccessToDictCubical(SuccessToDictBase):
    def __init__(self, index_to_level, cube_resolver, death_to_birth):
        super().__init__(index_to_level, death_to_birth)
        self.cube_resolver = cube_resolver

    @staticmethod
    def from_pdgm(pdgm):
        return SuccessToDictCubical(
            pdgm.index_to_level, pdgm.cubical_geometry_resolver, pdgm.death_index_to_birth_index
        )

    def __call__(self, success):
        if success is None:
            return None

        death = max(success.cell_indices)

        return dict(
            self.basedict(success, death),
            **{
                "points": self.cube_resolver.resolve_vertices(success.cell_indices),
                "cubes": self.cube_resolver.resolve_cells(success.cell_indices),
                "boundary": self.cube_resolver.resolve_cells(self.cube_resolver.boundary_cells(success.cell_indices)),
                "boundary-points": self.cube_resolver.resolve_vertices(
                    self.cube_resolver.boundary_cells(success.cell_indices)
                ),
                "children": self.children(death, success),
            },
        )


if __name__ == "__main__":
    main()
