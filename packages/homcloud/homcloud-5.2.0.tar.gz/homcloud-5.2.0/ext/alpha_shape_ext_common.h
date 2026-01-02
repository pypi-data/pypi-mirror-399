#ifndef HOMCLOUD_ALPHA_SHAPE_EXT_COMMON_H
#define HOMCLOUD_ALPHA_SHAPE_EXT_COMMON_H

static bool IsArrayValidPointCloud(PyArrayObject* points, int dim, int weighted) {
  if (PyArray_TYPE(points) != NPY_DOUBLE) {
    PyErr_SetString(PyExc_ValueError, "Array must be double for an alpha shape");
    return false;
  }

  if (PyArray_NDIM(points) != 2) {
    PyErr_SetString(PyExc_ValueError, "Array must be 2d for an alpha shape");
    return false;
  }

  if (PyArray_DIMS(points)[1] != dim + weighted) {
    PyErr_SetString(PyExc_ValueError, "Incorrect Array shape for an alpha shape");
    return false;
  }

  return true;
}

#endif // HOMCLOUD_ALPHA_SHAPE_EXT_COMMON_H
