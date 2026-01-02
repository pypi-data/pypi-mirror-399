import os

from PIL import Image
import numpy as np


def write_volume_slices(volumes, direction, spacer, slice_range, dirname):
    uppers = list(map(np.max, volumes))
    lowers = list(map(np.min, volumes))
    shape = volumes[0].shape[0:direction] + volumes[0].shape[direction + 1 :]
    width = shape[1] * len(volumes) + spacer * (len(volumes) - 1)
    height = shape[0]
    d = shape[1] + spacer
    if not slice_range:
        slice_range = (0, volumes[0].shape[direction])
    for n in range(*slice_range):
        array = np.zeros((height, width), dtype=np.uint8)
        for i, (volume, u, l) in enumerate(zip(volumes, uppers, lowers)):
            u_f = float(u)
            l_f = float(l)
            slice = slice_volume(volume, n, direction)
            array[:, d * i : d * i + shape[1]] = (slice - l_f) * 254 / (u_f - l_f)
        path = os.path.join(dirname, "{:04d}.png".format(n))
        Image.fromarray(array).save(path)


def slice_volume(volume, n, direction):
    if direction == 0:
        return volume[n, :, :]
    if direction == 1:
        return volume[:, n, :]
    if direction == 2:
        return volume[:, :, n]
    raise ValueError("{} is not valid for direction".format(n))
