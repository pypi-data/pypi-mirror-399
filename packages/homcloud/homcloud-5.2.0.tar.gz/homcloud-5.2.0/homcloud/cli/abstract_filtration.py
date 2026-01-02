import argparse

from homcloud.argparse_common import parse_bool
from homcloud.version import __version__
from homcloud.license import add_argument_for_license
from homcloud.abstract_filtration import AbstractFiltrationLoader


def main(args=None):
    args = args or argument_parser().parse_args()
    with open(args.input) as f:
        filt = AbstractFiltrationLoader.load_from(f, args.save_boundary_map)
    with open(args.output, "wb") as f:
        filt.compute_pdgm(f)


def argument_parser():
    p = argparse.ArgumentParser(description="Convert a description of boundary map to a PD")
    p.add_argument("-V", "--version", action="version", version=__version__)
    p.add_argument("-M", "--save-boundary-map", default=True, type=parse_bool, help="save boundary map")
    add_argument_for_license(p)
    p.add_argument("input", help="input file name")
    p.add_argument("output", help="output file name")
    return p


if __name__ == "__main__":
    main()
