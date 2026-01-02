import argparse
import json

import msgpack

from homcloud.version import __version__
import homcloud.pict.utils as utils
from homcloud.license import add_argument_for_license
from homcloud.pict.distance_transform import distance_transform
from homcloud.cli.pict.binarize_nd import binarize_picture
from homcloud.pict.tree import construct_mergetrees, construct_dict, save_pdgm


def argument_parser():
    p = argparse.ArgumentParser(description="Compute 0th PH tree and (n-1)-th PH tree")
    p.add_argument("-V", "--version", action="version", version=__version__)
    add_argument_for_license(p)
    p.add_argument(
        "-m",
        "--mode",
        required=True,
        help=("mode (white-base or black-base for binarize," + " superlevel or sublevel for levelset)"),
    )

    for_binarize = p.add_argument_group("for binarize")
    for_binarize.add_argument("-t", "--threshold", type=float, default=128)
    for_binarize.add_argument("--gt", type=float, default=None, help="lower threshold")
    for_binarize.add_argument("--lt", type=float, default=None, help="upper threshold")
    for_binarize.add_argument("-s", "--ensmall", action="store_true", default=False, help="ensmall binarized picture")
    for_binarize.add_argument(
        "--metric",
        default="manhattan",
        help="metric used to enlarge binarized image" " (manhattan(default), euclidean, etc.)",
    )
    # for_binarize.add_argument("--matrix", help="not implemnted yet")

    # arguments for input and output
    for_input_output = p.add_argument_group("for input and output")
    for_input_output.add_argument(
        "-T",
        "--type",
        default="text_nd",
        help="input data format " "(text2d, text_nd(default), picture2d, picture3d, npy)",
    )
    for_input_output.add_argument(
        "-O", "--output-type", default="pdgm", help="output file format " "(json, msgpack, pdgm(default))"
    )
    for_input_output.add_argument("-o", "--output", required=True, help="output file")
    p.add_argument("input", nargs="*", help="input files")
    return p


def main(args=None):
    args = args or argument_parser().parse_args()
    pict = utils.load_nd_picture(args.input, args.type)
    is_superlevel = args.mode == "superlevel"

    if args.mode in ["black-base", "white-base"]:
        binary_pict = binarize_picture(pict, args.threshold, args.mode, (args.gt, args.lt))
        bitmap = distance_transform(binary_pict, args.metric, args.ensmall)
    elif args.mode in ["sublevel", "superlevel"]:
        bitmap = pict
    else:
        raise RuntimeError("invalid mode")

    lower_mergetree, upper_mergetree = construct_mergetrees(bitmap, is_superlevel)
    dic = construct_dict(bitmap.ndim, is_superlevel, lower_mergetree, upper_mergetree)

    if args.output_type == "json":
        with open(args.output, "w") as f:
            json.dump(dic, f)
    elif args.output_type == "msgpack":
        with open(args.output, "wb") as f:
            msgpack.dump(dic, f, use_bin_type=True)
    elif args.output_type == "pdgm":
        with open(args.output, "wb") as f:
            save_pdgm(f, bitmap.ndim, is_superlevel, lower_mergetree, upper_mergetree)
    else:
        raise RuntimeError("Unknown output format: {}".format(args.output_type))


if __name__ == "__main__":
    main()
