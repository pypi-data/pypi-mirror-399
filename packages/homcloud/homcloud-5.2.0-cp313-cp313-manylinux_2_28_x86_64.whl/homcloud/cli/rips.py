import argparse

import numpy as np

from homcloud.rips import DistanceMatrix
from homcloud.version import __version__
from homcloud.license import add_argument_for_license
from homcloud.utils import load_symbols
from homcloud.argparse_common import parse_bool


def main(args=None):
    args = args or argument_parser().parse_args()
    matrix = DistanceMatrix(
        np.loadtxt(args.input), args.upper_degree, args.upper_value, load_symbols(args.vertex_symbols)
    )
    if args.save_boundary_map:
        filt = matrix.build_simplicial_filtration(True)
    else:
        filt = matrix.build_rips_filtration()

    with open(args.output, "wb") as f:
        filt.compute_pdgm(f, args.algorithm)


def argument_parser():
    p = argparse.ArgumentParser(description="Compute a PD from Vietris-Rips filtration")
    p.add_argument("-V", "--version", action="version", version=__version__)
    p.add_argument("-d", "--upper-degree", type=int, required=True, help="Maximum computed degree")
    p.add_argument("-u", "--upper-value", type=float, default=np.inf, help="Maximum distance (default: +inf)")
    p.add_argument("--vertex-symbols", help="vertex symbols file")
    p.add_argument(
        "-M",
        "--save-boundary-map",
        default=False,
        type=parse_bool,
        help="save boundary map into output file" "(only available with phat-* algorithms, on/*off*)",
    )
    p.add_argument("--algorithm", default=None, help="algorithm (ripser)")
    p.add_argument("--parallels", default=1, type=int, help="number of threads (default: 1)")
    add_argument_for_license(p)
    p.add_argument("input", help="input file")
    p.add_argument("output", help="output file")
    return p


if __name__ == "__main__":
    main()
