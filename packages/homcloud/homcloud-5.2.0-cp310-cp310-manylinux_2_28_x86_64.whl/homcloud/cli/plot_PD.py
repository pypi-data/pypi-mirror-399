import argparse
import sys

import matplotlib.pyplot as plt

import homcloud.pdgm as pdgm
from homcloud.version import __version__
from homcloud.argparse_common import add_arguments_for_load_diagrams, add_arguments_for_histogram_rulers
from homcloud.histogram import PDHistogram, Ruler
from homcloud.plot_PD import ZSpec, AuxPlotInfo, MarkerDrawer, PDPlotter


def main(args=None):
    """The main routine"""
    args = args or argument_parser().parse_args()
    pd = pdgm.load_merged_diagrams(args.input, args.type, args.degree)
    xy_rulers = Ruler.create_xy_rulers(args.x_range, args.xbins, args.y_range, args.ybins, pd)
    histogram = PDHistogram(pd, *xy_rulers)
    histogram.multiply_histogram(1.0 / args.normalize_constant)
    if args.diffuse_pairs:
        histogram.apply_gaussian_filter(args.diffuse_pairs)
    zspec = ZSpec.create_from_args(args)
    if args.title is None:
        args.title = args.input[0]
    aux_info = AuxPlotInfo.from_args(args)
    plotter = PDPlotter.find_plotter(args.style)(histogram, zspec, aux_info)

    fig, ax = plt.subplots()
    plotter.plot(fig, ax)

    if args.marker:
        MarkerDrawer.load_from_file(args.marker).draw(ax)

    if args.tight_layout or aux_info.require_tight_layout():
        plt.tight_layout()

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.show()

    plt.close(fig)


def argument_parser():
    parser = argparse.ArgumentParser(description="Plot a PD")
    parser.add_argument("-V", "--version", action="version", version=__version__)
    add_arguments_for_load_diagrams(parser)
    add_arguments_for_zspec(parser)
    parser.add_argument(
        "-s", "--style", default="colorhistogram", help="plotting style (colorhistogram(default), contour)"
    )
    add_arguments_for_auxinfo(parser)
    parser.add_argument(
        "-D",
        "--diffuse-pairs",
        metavar="SCATTERING_SIZE",
        type=float,
        default=None,
        help="Diffuse pairs using gaussian distribution of SD=SIGMA",
    )
    parser.add_argument("-o", "--output", help="output file")
    add_arguments_for_histogram_rulers(parser)
    parser.add_argument(
        "-n", "--normalize-constant", type=float, default=1.0, help="normalize constant to histogram height"
    )
    parser.add_argument("-M", "--marker", help="marker file")
    parser.add_argument(
        "--dpi", type=int, default=None, help="output DPI (used with -o option, default is savefig.dpi for matplotlib)"
    )
    parser.add_argument(
        "--tight-layout", action="store_true", default=False, help="use tight layout (adjusting layout)"
    )
    parser.add_argument("input", metavar="INPUT", nargs="+", help="Input file path")
    return parser


def add_arguments_for_zspec(parser):
    parser.add_argument(
        "-p", "--power", metavar="POWER", type=float, default=None, help="Output x^POWER for each value x"
    )
    parser.add_argument("-l", "--log", action="store_true", default=False, help="Output log(x+1) for each value x")
    parser.add_argument("--loglog", action="store_true", default=False, help="Output log(log(x+1)+1)")
    parser.add_argument("--linear-midpoint", type=float, help="linear with midpoint")
    parser.add_argument(
        "-m", "--vmax", metavar="MAX", type=float, default=None, help="Maximum of colorbar (default: autoscale)"
    )
    parser.add_argument("--vmin", type=float, default=None, help="Minimum of colorbar")
    parser.add_argument("-c", "--colormap", default=None, help="matplotlib colormap name")


def add_arguments_for_auxinfo(parser):
    parser.add_argument("-t", "--title", help="title string")
    parser.add_argument("-U", "--unit-name", help="The unit name of birth and death times")
    parser.add_argument("--font-size", help="font size (default: 12)")
    parser.add_argument("--aspect", default="auto", help="histogram aspect (default: auto)")
    parser.add_argument(
        "--plot-essential", action="store_true", help="whether to plot essential values (default: False)"
    )


if __name__ == "__main__":
    sys.exit(main())
