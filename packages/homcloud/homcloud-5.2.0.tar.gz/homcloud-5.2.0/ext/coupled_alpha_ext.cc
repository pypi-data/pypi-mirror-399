#include "homcloud_common.h"
#include "homcloud_cgal.h"
#include "homcloud_numpy.h"

#include <cstdint>
#include <vector>

#include <coupled_alpha.hpp>

using coupled_alpha::Simplex;

PyObject* simplex_to_tuple(const Simplex& s) {
  switch (s.size()) {
    case 0:
      return Py_BuildValue("()");
    case 1:
      return Py_BuildValue("(I)", s[0]);
    case 2:
      return Py_BuildValue("(II)", s[0], s[1]);
    case 3:
      return Py_BuildValue("(III)", s[0], s[1], s[2]);
    case 4:
      return Py_BuildValue("(IIII)", s[0], s[1], s[2], s[3]);
    case 5:
      return Py_BuildValue("(IIIII)", s[0], s[1], s[2], s[3], s[4]);
    default:
      PyErr_Format(PyExc_ValueError, "Invalid simplex size: %d", s.size());
      return nullptr;
  }
}

template<int D>
Eigen::Vector<double, D>
vector_from_array(PyArrayObject* ary, size_t i) {
  assert(0);
}

template<>
Eigen::Vector<double, 2>
vector_from_array<2>(PyArrayObject* ary, size_t i) {
  return Eigen::Vector2d{*GETPTR2D<double>(ary, i, 0), *GETPTR2D<double>(ary, i, 1)};
}

template<>
Eigen::Vector<double, 3>
vector_from_array<3>(PyArrayObject* ary, size_t i) {
  return Eigen::Vector3d{*GETPTR2D<double>(ary, i, 0), *GETPTR2D<double>(ary, i, 1), *GETPTR2D<double>(ary, i, 2)};
}

template<int D>
PyObject* compute(PyObject* self, PyObject* args) {
  PyArrayObject* X;
  PyArrayObject* Y;
  
  if (!PyArg_ParseTuple(args, "O!O!", &PyArray_Type, &X, &PyArray_Type, &Y))
    return nullptr;

  if (!IsArrayTypeDouble(X)) return nullptr;
  if (!IsArrayTypeDouble(Y)) return nullptr;

  if (PyArray_NDIM(X) != 2 || PyArray_NDIM(Y) != 2 || PyArray_DIMS(X)[1] != D || PyArray_DIMS(Y)[1] != D) {
    PyErr_Format(PyExc_ValueError, "Data must be (N,%d) array", D);
    return nullptr;
  }

  
  std::vector<uint8_t> labels;
  std::vector<Eigen::Vector<double, D>> coords;

  for (int i = 0; i < PyArray_DIMS(X)[0]; ++i) {
    labels.push_back(0);
    coords.push_back(vector_from_array<D>(X, i));
  }

  for (int i = 0; i < PyArray_DIMS(Y)[0]; ++i) {
    labels.push_back(1);
    coords.push_back(vector_from_array<D>(Y, i));
  }
  
  coupled_alpha::CoupledAlpha<D> ca(coords, labels);
  const auto values = ca.compute();

  PyObject* ret = PyDict_New();
  if (!ret) return nullptr;

  PyObject* key = nullptr;
  PyObject* val = nullptr;

  for (size_t d = 0; d <= D + 1; ++d) {
    for (const auto& [simplex, value]: values[d]) {
      key = simplex_to_tuple(simplex);
      if (!key) goto error;
      val = PyFloat_FromDouble(value);
      if (!val) goto error;
      
      int r = PyDict_SetItem(ret, key, val);
      Py_XDECREF(key); key = nullptr;
      Py_XDECREF(val); key = nullptr;
      
      if (r < 0) goto error;
    }
  }

  return ret;
  
 error:
    Py_XDECREF(ret);
    Py_XDECREF(key);
    Py_XDECREF(val);
  return nullptr;
}


static PyMethodDef coupled_alpha_ext_Methods[] = {
  {"compute_2d", compute<2>, METH_VARARGS, "Computing coupled alpha for 2d pointcloud"},
  {"compute_3d", compute<3>, METH_VARARGS, "Computing coupled alpha for 3d pointcloud"},
  {NULL, NULL, 0, NULL}
};

static PyModuleDef coupled_alpha_ext_Module = {
  PyModuleDef_HEAD_INIT,
  "homcloud.coupled_alpha_ext",
  "The module for 2D/3D Coupled Alpha shapes",
  -1,
  coupled_alpha_ext_Methods,
};

PyMODINIT_FUNC
PyInit_coupled_alpha_ext()
{
  PyObject* module = PyModule_Create(&coupled_alpha_ext_Module);
  if (!module)
    return NULL;

  import_array();
  
  return module;
}
