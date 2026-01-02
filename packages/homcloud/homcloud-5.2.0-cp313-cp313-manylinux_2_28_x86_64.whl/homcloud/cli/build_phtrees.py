import argparse
import sys

import msgpack
import numpy as np

from homcloud.version import __version__
from homcloud.license import add_argument_for_license
from homcloud.utils import load_symbols
from homcloud.build_phtrees import PHTrees


def argument_parser():
    p = argparse.ArgumentParser(description="Comput a PH trees from a point cloud")
    p.add_argument("-V", "--version", action="version", version=__version__)
    p.add_argument("-d", "--dimension", type=int, required=True, help="dimension of the input data")
    p.add_argument("--vertex-symbols", help="vertex symbols file")
    p.add_argument("-w", "--weighted", action="store_true", default=False, help="use an weighted alpha filtration")
    p.add_argument(
        "--no-square",
        action="store_true",
        default=False,
        help="no squared output, if a birth radius is negative, the output is -sqrt(abs(r))",
    )
    p.add_argument("--square", action="store_const", const=False, dest="no_square")
    p.add_argument("--input-type", help="input type (pdgm/pointcloud)")
    add_argument_for_license(p)
    p.add_argument("input")
    p.add_argument("output")
    return p


def main(args=None):
    from homcloud.alpha_filtration import AlphaFiltration

    args = args or argument_parser().parse_args()
    pointcloud = np.loadtxt(args.input)

    filt = AlphaFiltration.create(
        pointcloud, args.dimension, args.weighted, None, args.no_square, load_symbols(args.vertex_symbols), True
    )

    matrix = filt.build_phat_matrix()
    boundary_map = msgpack.loads(matrix.boundary_map_byte_sequence(), raw=False)

    trees = PHTrees(args.dimension, boundary_map["map"])
    with open(args.output, "wb") as f:
        trees.save_pdgm(f, filt)


if __name__ == "__main__":
    sys.exit(main())
