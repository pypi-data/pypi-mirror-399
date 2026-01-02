import numpy as np


def transform_to_x_axis(v1, v2):
    d = v2 - v1
    norm = np.linalg.norm(d)
    rotation = np.array([[d[0], d[1]], [-d[1], d[0]]]) / norm
    scale_x = np.array(([1 / norm, 0], [0, 1]))
    return v1, np.dot(scale_x, rotation)


def construct_label(labelstr, birth, death):
    if labelstr is None:
        return "({:4f},{:4f})".format(birth, death)
    else:
        return labelstr
