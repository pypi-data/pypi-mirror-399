#include "homcloud_common.h"
#include "homcloud_cgal.h"
#include "homcloud_numpy.h"
#include "alpha_shape_ext_common.h"

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

#include <CGAL/Regular_triangulation_2.h>
#include <CGAL/Alpha_shape_2.h>
#include <CGAL/Triangulation_vertex_base_with_info_2.h>

struct VertexInfo {
  int index;
};

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel;

typedef CGAL::Regular_triangulation_vertex_base_2<Kernel> Rvb;
typedef CGAL::Triangulation_vertex_base_with_info_2<VertexInfo, Kernel, Rvb> Vinfo;
typedef CGAL::Alpha_shape_vertex_base_2<Kernel, Vinfo> Vb;
typedef CGAL::Regular_triangulation_face_base_2<Kernel> Rf;
typedef CGAL::Alpha_shape_face_base_2<Kernel, Rf>  Fb;
typedef CGAL::Triangulation_data_structure_2<Vb, Fb> Tds;
typedef CGAL::Regular_triangulation_2<Kernel, Tds> Triangulation_2;
typedef CGAL::Alpha_shape_2<Triangulation_2>  AlphaShape2;

using Weighted_point = AlphaShape2::Weighted_point;
using Bare_point = AlphaShape2::Bare_point;
using Vertex_handle = AlphaShape2::Vertex_handle;
using Finite_edges_iterator = AlphaShape2::Finite_edges_iterator;
using Face_handle = AlphaShape2::Face_handle;
using PointWithInfo = std::pair<Weighted_point, VertexInfo>;

static std::vector<PointWithInfo> BuildPointCloud(PyArrayObject* array, int weighted) {
  std::vector<PointWithInfo> points;
  int npoints = PyArray_DIMS(array)[0];

  for (int i = 0; i < npoints; ++i) {
    double x = *GETPTR2D<double>(array, i, 0);
    double y = *GETPTR2D<double>(array, i, 1);
    double w = weighted ? *GETPTR2D<double>(array, i, 2) : 0.0;
    points.emplace_back(Weighted_point(Bare_point(x, y), w), VertexInfo{i});
  }
  return points;
}

static int NumSimplices(const AlphaShape2& alpha_shape) {
  return alpha_shape.number_of_vertices() +
      std::distance(alpha_shape.finite_edges_begin(), alpha_shape.finite_edges_end()) +
      alpha_shape.number_of_faces();
  return 0;
}

static PyObject* CreateSimplexAlphaPairForVertex(Vertex_handle h) {
  return Py_BuildValue("((i)d)", h->info().index, -(h->point().weight()));
}

static PyObject* CreateSimplexAlphaPairForEdge(const AlphaShape2& alpha_shape, Finite_edges_iterator it) {
  int v1 = it->first->vertex((it->second + 1) % 3)->info().index;
  int v2 = it->first->vertex((it->second + 2) % 3)->info().index;
  int w1 = std::min(v1, v2);
  int w2 = std::max(v1, v2);
  double a1 = it->first->get_ranges(it->second).get<0>();
  double a2 = it->first->get_ranges(it->second).get<1>();
  double a = (a1 > 0) ? a1 : a2;
  
  return Py_BuildValue("((ii)d)", w1, w2, a);
}

static PyObject* CreateSimplexAlphaPairForFace(const AlphaShape2& alpha_shape, Face_handle it) {
  std::array<int, 3> vertices;
  for (int i = 0; i < 3; ++i) {
    vertices[i] = it->vertex(i)->info().index;
  }
  std::sort(vertices.begin(), vertices.end());
  return Py_BuildValue("((iii)d)", vertices[0], vertices[1], vertices[2], it->get_alpha());
}


static PyObject* compute(PyObject *self, PyObject *args) {
  PyArrayObject* array;
  int weighted;
  
  if (!PyArg_ParseTuple(args, "O!p", &PyArray_Type, &array, &weighted))
    return NULL;

  if (!(IsArrayValidPointCloud(array, 2, weighted)))
    return NULL;

  std::vector<PointWithInfo> points = BuildPointCloud(array, weighted);

  Triangulation_2 triangulation(points.begin(), points.end());
  AlphaShape2 alpha_shape(triangulation, 0, AlphaShape2::GENERAL);
  
  PyObject* simplex_alpha_pairs = PyList_New(NumSimplices(alpha_shape));
  if (!simplex_alpha_pairs) goto error;

  int i;
  
  i = 0;
  for (auto it = alpha_shape.finite_vertices_begin(); it != alpha_shape.finite_vertices_end(); ++it, ++i) {
    PyObject* pair = CreateSimplexAlphaPairForVertex(it);
    if (!pair) goto error;
    PyList_SetItem(simplex_alpha_pairs, i, pair);
  }

  for (auto it = alpha_shape.finite_edges_begin(); it != alpha_shape.finite_edges_end(); ++it, ++i) {
    PyObject* pair = CreateSimplexAlphaPairForEdge(alpha_shape, it);
    if (!pair) goto error;
    PyList_SetItem(simplex_alpha_pairs, i, pair);
  }

  for (auto it = alpha_shape.finite_faces_begin(); it != alpha_shape.finite_faces_end(); ++it, ++i) {
    PyObject* pair = CreateSimplexAlphaPairForFace(alpha_shape, it);
    if (!pair) goto error;
    PyList_SetItem(simplex_alpha_pairs, i, pair);
  }

  return simplex_alpha_pairs;
error:
  Py_XDECREF(simplex_alpha_pairs);
  return NULL;
}

static PyMethodDef alpha_shape2_ext_functions[] = {
  {"compute", (PyCFunction)compute, METH_VARARGS, "Compute a 2D alpha shape"},
  {NULL, NULL, 0, NULL}
};
  
static PyModuleDef alpha_shape2_ext_module = {
  PyModuleDef_HEAD_INIT,
  "homcloud.alpha_shape2_ext",
  "The C++ module for 2D Alpha shape",
  -1,
  alpha_shape2_ext_functions
};

PyMODINIT_FUNC
PyInit_alpha_shape2_ext() {
  PyObject* module = PyModule_Create(&alpha_shape2_ext_module);
  if (!module)
    return NULL;

  import_array();

  return module;
}
