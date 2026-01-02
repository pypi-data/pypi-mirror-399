import argparse
from tempfile import TemporaryDirectory
import os
import subprocess
import re
from operator import attrgetter
import operator
import json

import numpy as np
from PIL import Image

from homcloud.pict.show_birthdeath_pixels_2d import setup_images, Pair
from homcloud.version import __version__
from homcloud.pdgm import PDGM
from homcloud.argparse_common import parse_color
from homcloud.histogram import Histogram


RE_PREDICATE_PAIR = re.compile(r"(lifetime|birth|death)\s*(>|<|>=|<=|==)\s*(-?\d+\.?\d*)")
OPERATORS = {">": operator.gt, "<": operator.lt, ">=": operator.ge, "<=": operator.le, "==": operator.eq}


def main(args=None):
    """Main routine of this module"""
    args = args or argument_parser().parse_args()
    pd = PDGM.open(args.diagram, args.degree)
    predicates = [predicate_from_string(string) for string in args.filter]
    if use_vectorized_histogram_mask(args):
        predicates.append(histogram_mask_predicate(args))

    pairs = [pair for pair in pairs_positions(pd) if all_true(predicates, pair)]
    output_image, marker_drawer = setup_images(open_image(args.picture), args.scale, args.no_label)
    marker_drawer.setup_by_args(args)

    for pair in pairs:
        marker_drawer.draw_pair(pair)

    if args.output:
        output_image.save(args.output)
    else:
        display_picture(args.show_command, output_image)


def argument_parser():
    """Return ArgumentParser object used in this program."""
    p = argparse.ArgumentParser(description="Show birth and death cubes in a 2D picture")
    p.add_argument("-V", "--version", action="version", version=__version__)
    p.add_argument("-d", "--degree", type=int, required=True, help="degree of PH")
    p.add_argument("-f", "--filter", action="append", default=[], help='filters (ex: "lifetime > 5.0")')
    p.add_argument("-v", "--vectorized-histogram-mask", help="0-1 vector textfile for mask")
    p.add_argument("-H", "--histoinfo", help="vectorize histogram information (both -V and -H are required)")
    p.add_argument("-B", "--birth", default=False, action="store_true", help="plot birth pixels")
    p.add_argument("-D", "--death", default=False, action="store_true", help="plot death pixels")
    p.add_argument("-L", "--line", default=False, action="store_true", help="draw line between death and birth pixels")
    p.add_argument("-s", "--scale", default=1, type=int, help="image scaling factor (1, 3, 5, ...)")
    p.add_argument(
        "-M",
        "--marker-type",
        default="filled-diamond",
        help="marker type (point, filled-diamond(default), square, filled-square, circle, filled-circle)",
    )
    p.add_argument("-S", "--marker-size", default=1, type=int, help="marker size (default: 1)")
    p.add_argument("--show-command", default="eog", help="image display command")
    p.add_argument("--no-label", default=False, action="store_true", help="birth-death labels are not drawn")
    p.add_argument("--birth-color", type=parse_color, default=(255, 0, 0), help="birth pixel color")
    p.add_argument("--death-color", type=parse_color, default=(0, 0, 255), help="death pixel color")
    p.add_argument("--line-color", type=parse_color, default=(0, 255, 0), help="birth-death line color")
    p.add_argument("-o", "--output", help="output filername")
    p.add_argument("picture", help="input Picture file name")
    p.add_argument("diagram", help="persistence diagram file name")
    return p


def predicate_from_string(string):
    """Create a predicate from string

    Example:
    filter_from_string("lifetime > 5.0") # => lambda pair: pair.lifetime > 5.0
    """
    m = RE_PREDICATE_PAIR.match(string)
    if not m:
        return None
    attr = attrgetter(m.group(1))
    op = OPERATORS[m.group(2)]
    threshold = float(m.group(3))
    return lambda x: op(attr(x), threshold)


def use_vectorized_histogram_mask(args):
    if args.vectorized_histogram_mask and args.histoinfo:
        return True
    if (args.vectorized_histogram_mask is None) and (args.histoinfo is None):
        return False
    print("Both -v and -H options are required")
    exit(1)


def histogram_mask_predicate(args):
    vector = np.loadtxt(args.vectorized_histogram_mask, dtype=bool)
    with open(args.histoinfo) as f:
        histoinfo = json.load(f)
    histogram = Histogram.reconstruct_from_vector(vector, histoinfo)

    def predicate(pair):
        return histogram.value_at(pair.birth, pair.death)

    return predicate


def all_true(predicates, obj):
    """Return True for all predicates returns True"""
    return all(predicate(obj) for predicate in predicates)


def pairs_positions(pd):
    return (Pair(*args) for args in zip(pd.births, pd.deaths, pd.birth_positions, pd.death_positions))


def open_image(path):
    """Open image file and convert it to accept colored drawings"""
    return Image.open(path).convert("RGB")


def display_picture(command, image):
    """Display image to your display

    Args:
    command -- command name string to display image (for example, eog)
    image -- image object (PIL.Image)
    """
    with TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "tmp.png")
        image.save(path)
        subprocess.call([command, path])


if __name__ == "__main__":
    main()
