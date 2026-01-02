from functools import partial
import re
from bisect import bisect

import numpy as np
import pulp


try:
    from pulp.solvers import PulpSolverError
except ImportError:
    from pulp.apis.core import PulpSolverError


RE_OLD_SOLVER_NAME = re.compile(r"^[a-z\-]+\Z")


def find_lp_solver(solver, options):
    if solver is None:
        return default_lp_solver()

    if isinstance(solver, pulp.apis.LpSolver):
        return solver

    if RE_OLD_SOLVER_NAME.match(solver):
        solver = solver.upper().replace("-", "_")
        if solver == "COIN":
            solver = "COIN_CMD"

    try:
        return pulp.getSolver(solver, **options)
    except PulpSolverError as e:
        raise RuntimeError(str(e))


def default_lp_solver():
    lp_solver = pulp.LpSolverDefault.copy()
    lp_solver.msg = 0
    return lp_solver


def sign_function(boundary_map):
    def sign_simplicial(i, kth):
        return -1 if kth % 2 else 1

    def sign_abstract(i, kth):
        return boundary_map["map"][i][2][kth]

    def sign_cubical(i, kth):
        return -1 if (kth % 4) in (1, 2) else 1

    if boundary_map["type"] == "simplicial":
        return sign_simplicial
    if boundary_map["type"] == "abstract":
        return sign_abstract
    if boundary_map["type"] == "cubical":
        return sign_cubical

    raise RuntimeError("Unknown maptype: {}".format(boundary_map["type"]))


class Optimizer:
    def __init__(self, birth, death, boundary_map, lp_solver):
        self.birth = birth
        self.death = death
        self.boundary_map = boundary_map
        self.lp_solver = lp_solver

    def build_partial_boundary_matrix(self, is_active_cell):
        map = self.boundary_map["map"]
        sign = sign_function(self.boundary_map)

        def dim(i):
            return map[i][0]

        degree = dim(self.death) - 1
        partial_map = dict()
        lpvars = []

        for i in range(self.birth, self.death + 1):
            if dim(i) == degree:
                partial_map[i] = list()
            elif dim(i) == degree + 1 and is_active_cell(i):
                lpvars.append(i)
                for kth, j in enumerate(map[i][1]):
                    if j in partial_map:
                        partial_map[j].append((sign(i, kth), i))

        return lpvars, partial_map

    def build_lp_problem(self, lpvar_indices, partial_map):
        prob = pulp.LpProblem("OptimalVolume", pulp.LpMinimize)
        xs = pulp.LpVariable.dicts("x", (lpvar_indices,), -1, 1, "Continuous")
        ys = pulp.LpVariable.dicts("y", (lpvar_indices,), 0, 1, "Continuous")

        prob.setObjective(pulp.lpSum(ys.values()))

        for i in lpvar_indices:
            prob.addConstraint(xs[i] - ys[i] <= 0.0)
            prob.addConstraint(xs[i] + ys[i] >= 0.0)

        for low, constraint in partial_map.items():
            if not constraint:
                continue
            if low == self.birth:
                continue
            prob.addConstraint(pulp.lpSum(s * xs[i] for (s, i) in constraint) == 0)

        prob.addConstraint(xs[self.death] == 1)

        return prob, ys

    def find(self, is_active_cell=lambda _: True):
        lpvars, partial_map = self.build_partial_boundary_matrix(is_active_cell)
        prob, ys = self.build_lp_problem(lpvars, partial_map)
        try:
            status = prob.solve(self.lp_solver)
        except PulpSolverError as err:
            # workaround for cplex and pulp
            if re.search("infeasible", err.args[0]):
                return Failure(pulp.LpStatusInfeasible)
            else:
                raise err

        if status == pulp.LpStatusOptimal:
            return Success(self.optimal_volume_cell_indices(ys))
        else:
            return Failure(status)

    @staticmethod
    def optimal_volume_cell_indices(ys):
        return [index for (index, var) in ys.items() if var.varValue >= 0.00001]


class Success:
    def __init__(self, cell_indices):
        self.cell_indices = cell_indices
        self.pair = None
        self.subvolume = None

    success = True
    infeasible = False

    def children(self, death, death_to_birth):
        def valid(c):
            return c != death and c in death_to_birth

        return [(death_to_birth[c], c) for c in self.cell_indices if valid(c)]

    def __repr__(self):
        return "<optvol.Success: {}>".format(self.cell_indices)


class Failure:
    def __init__(self, status):
        self.status = status
        self.pair = None

    success = False

    @property
    def infeasible(self):
        # NOTE: GLPK solver returns pulp.LpStatusUndefined when a problem is infeasible.
        # Therefore pulp.LpStatusUndefined is treated as an infeasible failure.
        # This is an workaround for GLPK.
        return self.status in [pulp.LpStatusInfeasible, pulp.LpStatusUndefined]

    @property
    def message(self):
        msg = pulp.LpStatus[self.status]
        if self.pair:
            return "{} at ({}, {})".format(msg, *self.pair)
        else:
            return msg

    def __repr__(self):
        return "<optvol.Failure: {}>".format(self.message)

    def draw(self, drawer, coord_resolver, volume_color, boundary_color, index):
        pass


class RetryOptimizer:
    def __init__(self, optimizer, is_active_cell, times):
        self.optimizer = optimizer
        self.is_active_cell = is_active_cell
        self.times = times

    def find(self):
        for n in range(self.times):
            result = self.optimizer.find(partial(self.is_active_cell, n))
            if result.infeasible:
                pass
            else:
                return result

        return result  # This line always returns infeasible result


def is_active_cell(coord_resolver, center, threshold, n, cell_index):
    if threshold is None:
        return True
    centroid = np.array(coord_resolver.centroid(cell_index))
    return np.linalg.norm(center - centroid) < threshold * (2**n)


class OptimizerBuilder:
    def __init__(self, degree, boundary_map, lp_solver):
        self.degree = degree
        self.boundary_map = boundary_map
        self.lp_solver = lp_solver

    def build(self, birth, death):
        return Optimizer(birth, death, self.boundary_map, self.lp_solver)

    def to_query_dict(self):
        return {"degree": self.degree, "solver-name": self.solver_name, "solver-options": self.solver_options}

    @property
    def solver_name(self):
        return self.lp_solver.__class__.__name__

    @property
    def solver_options(self):
        if hasattr(self.lp_solver, "getOptions"):
            return self.lp_solver.getOptions()
        else:
            return None

    @staticmethod
    def from_alpha_pdgm(pdgm, cutoff_radius, retry, lp_solver):
        return RetryOptimizerBuilder(
            pdgm.degree, pdgm.boundary_map_chunk, lp_solver, pdgm.alpha_coord_resolver, cutoff_radius, retry
        )

    @staticmethod
    def from_cubical_pdgm(pdgm, cutoff_radius, retry, lp_solver):
        return RetryOptimizerBuilder(
            pdgm.degree, pdgm.boundary_map_chunk, lp_solver, pdgm.cubical_geometry_resolver, cutoff_radius, retry
        )

    def builder_without_retry(self):
        return self


class RetryOptimizerBuilder(OptimizerBuilder):
    def __init__(self, degree, boundary_map, lp_solver, coord_resolver, cutoff, retry):
        super().__init__(degree, boundary_map, lp_solver)
        self.coord_resolver = coord_resolver
        self.cutoff = cutoff
        self.retry = retry

    def build(self, birth, death):
        return RetryOptimizer(
            super().build(birth, death),
            partial(is_active_cell, self.coord_resolver, self.coord_resolver.centroid(death), self.cutoff),
            self.retry,
        )

    def to_query_dict(self):
        return dict(
            super().to_query_dict(),
            **{
                "cutoff-radius": self.cutoff,
                "num-retry": self.retry,
            },
        )

    def builder_without_retry(self):
        return OptimizerBuilder(self.degree, self.boundary_map, self.lp_solver)


def bisect_tightened(b, d, index_to_level, epsilon):
    k = bisect(index_to_level, index_to_level[b] + epsilon, lo=b, hi=d + 1)
    assert k <= d, "epsilon must be smaller than lifetime"
    # 次の行で k - 1 を使っているのは，Optimizer.build_lp_problemで
    # if low == self.birth:
    #      continue
    # となっている部分と整合性を取るため
    return k - 1


class TightenedVolumeFinder:
    def __init__(self, optimizer_builder, index_to_level, epsilon):
        self.optimizer_builder = optimizer_builder
        self.index_to_level = index_to_level
        self.epsilon = epsilon

    def find(self, birth, death):
        k = bisect_tightened(birth, death, self.index_to_level, self.epsilon)
        return self.optimizer_builder.build(k, death).find()

    def to_query_dict(self):
        return dict(self.optimizer_builder.to_query_dict(), **{"query-target": "tightened-volume"})


class OptimalVolumeFinder:
    def __init__(self, optimizer_builder):
        self.optimizer_builder = optimizer_builder

    def find(self, birth, death):
        return self.optimizer_builder.build(birth, death).find()

    def to_query_dict(self):
        return dict(self.optimizer_builder.to_query_dict(), **{"query-target": "optimal-volume"})


class TightenedSubVolumeFinder:
    def __init__(self, optimizer_builder, index_to_level, epsilon):
        self.optimizer_builder = optimizer_builder
        self.index_to_level = index_to_level
        self.epsilon = epsilon

    def find(self, birth, death, optimal_volume_cells):
        k = bisect_tightened(birth, death, self.index_to_level, self.epsilon)
        return self.optimizer_builder.build(k, death).find(
            partial(self.is_active_cell_for_tightend_subvolume, birth, optimal_volume_cells)
        )

    def is_active_cell_for_tightend_subvolume(self, birth, optimal_volume_cells, cell_index):
        return cell_index in optimal_volume_cells and (
            self.index_to_level[birth] + self.epsilon < self.index_to_level[cell_index]
        )


class OptimalVolumeTightenedSubVolumeFinder:
    def __init__(self, optimizer_builder, index_to_level, epsilon):
        self.optimizer_builder = optimizer_builder
        self.tsv_finder = TightenedSubVolumeFinder(optimizer_builder.builder_without_retry(), index_to_level, epsilon)

    def find(self, birth, death):
        optimal_volume = self.optimizer_builder.build(birth, death).find()
        if not optimal_volume.success:
            return optimal_volume
        optimal_volume.subvolume = self.tsv_finder.find(birth, death, optimal_volume.cell_indices)
        return optimal_volume

    def to_query_dict(self):
        return dict(self.optimizer_builder.to_query_dict(), **{"query-target": "tightened-subvolume"})


class OptimalVolumeError(Exception):
    """Base class for expretions in homcloud.optimal_volume"""

    def __init__(self, message, code):
        self.message = message
        self.code = code


class InfeasibleError(OptimalVolumeError):
    """Exception raised for errors for LpstatusInfeasible."""

    def __init__(self, message, code):
        super().__init__(message, code)
