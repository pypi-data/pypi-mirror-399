#include "homcloud_common.h"
#include "homcloud_numpy.h"

bool homcloud_IsArrayTypeDouble(PyArrayObject* points) {
  if (PyArray_TYPE(points) == NPY_DOUBLE)
    return true;

  PyErr_SetString(PyExc_TypeError, "Array must be double");
  return false;
}
