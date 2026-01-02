from tempfile import TemporaryDirectory
import subprocess
import argparse
import re

import numpy as np

from homcloud.pict.slice3d import write_volume_slices


def main(args=None):
    args = args or argument_parser().parse_args()
    volumes = [np.load(path) for path in args.input]

    assert [volume.shape == volumes[0].shape for volume in volumes]

    if args.slice is not None:
        with TemporaryDirectory() as tmpdir:
            write_volume_slices(volumes, args.slice, args.spacer, args.range, tmpdir)
            subprocess.call("{} {}".format(args.image_viewer, tmpdir), shell=True)


def argument_parser():
    p = argparse.ArgumentParser(description="3d npy data viewer")
    p.add_argument("-s", "--slice", default=0, type=int, help="slicing direction (0, 1, or 2)")
    p.add_argument("-S", "--spacer", default=10, type=int, help="spacer pixels")
    p.add_argument("-r", "--range", default=None, type=parse_range, help="range of slices")
    p.add_argument("--image-viewer", default="eog -n", help="image viewer program name")
    p.add_argument("input", nargs="+", help="input files")
    return p


def parse_range(string):
    l, r = re.split(r":", string)
    return int(l), int(r)


if __name__ == "__main__":
    main()
