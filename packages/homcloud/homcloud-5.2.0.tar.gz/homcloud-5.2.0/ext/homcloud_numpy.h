// -*- mode: c++ -*-
#ifndef HOMCLOUD_NUMPY_H
#define HOMCLOUD_NUMPY_H

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

template<class T> PyObject* cast_PyObj(T* obj) {
  return reinterpret_cast<PyObject*>(obj);
}

bool homcloud_IsArrayTypeDouble(PyArrayObject* points);
#define IsArrayTypeDouble homcloud_IsArrayTypeDouble

template<typename T>
T* GETPTR1D(PyArrayObject* ary, npy_intp i) {
  return reinterpret_cast<T*>(PyArray_GETPTR1(ary, i));
}

template<typename T>
T* GETPTR2D(PyArrayObject* ary, npy_intp i, npy_intp j) {
  return reinterpret_cast<T*>(PyArray_GETPTR2(ary, i, j));
}


#endif // HOMCLOUD_NUMPY_H
