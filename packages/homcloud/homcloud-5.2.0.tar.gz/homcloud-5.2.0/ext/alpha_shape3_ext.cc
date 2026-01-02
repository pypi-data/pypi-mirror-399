#include "homcloud_common.h"
#include "homcloud_cgal.h"
#include "homcloud_numpy.h"
#include "alpha_shape_ext_common.h"

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Regular_triangulation_3.h>
#include <CGAL/Alpha_shape_3.h>
#include <CGAL/Triangulation_vertex_base_with_info_3.h>
#include <CGAL/Alpha_shape_cell_base_3.h>
#include <CGAL/Alpha_shape_vertex_base_3.h>

struct VertexInfo {
  int index;
};

using Kernel =CGAL::Exact_predicates_inexact_constructions_kernel;
using Rvb = CGAL::Regular_triangulation_vertex_base_3<Kernel>;
using Vinfo = CGAL::Triangulation_vertex_base_with_info_3<VertexInfo, Kernel, Rvb>;
using Vb = CGAL::Alpha_shape_vertex_base_3<Kernel,Vinfo>;
using Rcb = CGAL::Regular_triangulation_cell_base_3<Kernel>;
using Cb = CGAL::Alpha_shape_cell_base_3<Kernel,Rcb>;
using Tds = CGAL::Triangulation_data_structure_3<Vb,Cb>;
using Triangulation = CGAL::Regular_triangulation_3<Kernel,Tds>;
using AlphaShape3 = CGAL::Alpha_shape_3<Triangulation>;

using Weighted_point = AlphaShape3::Weighted_point;
using Bare_point = AlphaShape3::Bare_point;
using PointWithInfo = std::pair<Weighted_point, VertexInfo>;
using Vertex_handle = AlphaShape3::Vertex_handle;
using Finite_edges_iterator = AlphaShape3::Finite_edges_iterator;
using Finite_facets_iterator = AlphaShape3::Finite_facets_iterator;
using Cell_handle = AlphaShape3::Cell_handle;

static std::vector<PointWithInfo> BuildPointCloud(PyArrayObject* array, int weighted) {
  std::vector<PointWithInfo> points;
  int npoints = PyArray_DIMS(array)[0];

  for (int i = 0; i < npoints; ++i) {
    double x = *GETPTR2D<double>(array, i, 0);
    double y = *GETPTR2D<double>(array, i, 1);
    double z = *GETPTR2D<double>(array, i, 2);
    double w = weighted ? *GETPTR2D<double>(array, i, 3) : 0.0;
    points.emplace_back(Weighted_point(Bare_point(x, y, z), w), VertexInfo{i});
  }
  return points;
}

static Py_ssize_t NumSimplices(const AlphaShape3& alpha_shape) {
  return alpha_shape.number_of_vertices() + alpha_shape.number_of_finite_edges() +
      alpha_shape.number_of_finite_facets() + alpha_shape.number_of_finite_cells();
}

static double AlphaValue(const CGAL::Alpha_status<double>& status) {
  return status.is_Gabriel() ? status.alpha_min() : status.alpha_mid();
}

static PyObject* CreateSimplexAlphaPairForVertex(Vertex_handle h) {
  return Py_BuildValue("((i)d)", h->info().index, -(h->point().weight()));
}

static PyObject* CreateSimplexAlphaPairForEdge(const AlphaShape3& alpha_shape, Finite_edges_iterator it) {
  int v1 = it->first->vertex(it->second)->info().index;
  int v2 = it->first->vertex(it->third)->info().index;
  int w1 = std::min(v1, v2);
  int w2 = std::max(v1, v2);
  double a = AlphaValue(alpha_shape.get_alpha_status(*it));
  
  return Py_BuildValue("((ii)d)", w1, w2, a);
}

static PyObject* CreateSimplexAlphaPairForFacet(const AlphaShape3& alpha_shape, Finite_facets_iterator it) {
  static const int facet_indices[4][3] = {
    {1,2,3},
    {2,3,0},
    {3,0,1},
    {0,1,2},
  };

  Cell_handle cell = it->first;
  int v = it->second;
  double a = AlphaValue(alpha_shape.get_alpha_status(*it));
  std::array<int, 3> vertices;
  
  for (int i = 0; i < 3; ++i) {
    vertices[i] = cell->vertex(facet_indices[v][i])->info().index;
  }
  std::sort(vertices.begin(), vertices.end());

  return Py_BuildValue("((iii)d)", vertices[0], vertices[1], vertices[2], a);
}

static PyObject* CreateSimplexAlphaPairForCell(const AlphaShape3& alpha_shape, Cell_handle it) {
  std::array<int, 4> vertices;
  for (int i = 0; i < 4; ++i) {
    vertices[i] = it->vertex(i)->info().index;
  }
  std::sort(vertices.begin(), vertices.end());
  return Py_BuildValue("((iiii)d)", vertices[0], vertices[1], vertices[2], vertices[3], it->get_alpha());
}

static PyObject* compute(PyObject *self, PyObject *args) {
  PyArrayObject* array;
  int weighted;
  
  if (!PyArg_ParseTuple(args, "O!p", &PyArray_Type, &array, &weighted))
    return NULL;

  if (!(IsArrayValidPointCloud(array, 3, weighted)))
    return NULL;

  std::vector<PointWithInfo> points = BuildPointCloud(array, weighted);
  Triangulation triangulation(points.begin(), points.end());
  AlphaShape3 alpha_shape(triangulation, 0, AlphaShape3::GENERAL);

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

  for (auto it = alpha_shape.finite_facets_begin(); it != alpha_shape.finite_facets_end(); ++it, ++i) {
    PyObject* pair = CreateSimplexAlphaPairForFacet(alpha_shape, it);
    if (!pair) goto error;
    PyList_SetItem(simplex_alpha_pairs, i, pair);
  }

  for (auto it = alpha_shape.finite_cells_begin(); it != alpha_shape.finite_cells_end(); ++it, ++i) {
    PyObject* pair = CreateSimplexAlphaPairForCell(alpha_shape, it);
    if (!pair) goto error;
    PyList_SetItem(simplex_alpha_pairs, i, pair);
  }

  return simplex_alpha_pairs;
  
error:
  Py_XDECREF(simplex_alpha_pairs);
  return NULL;
  
}

static PyMethodDef alpha_shape3_ext_functions[] = {
  {"compute", (PyCFunction)compute, METH_VARARGS, "Compute a 3D alpha shape"},
  {NULL, NULL, 0, NULL}
};
  
static PyModuleDef alpha_shape3_ext_module = {
  PyModuleDef_HEAD_INIT,
  "homcloud.alpha_shape3_ext",
  "The C++ module for 3D Alpha shape",
  -1,
  alpha_shape3_ext_functions
};

PyMODINIT_FUNC
PyInit_alpha_shape3_ext() {
  PyObject* module = PyModule_Create(&alpha_shape3_ext_module);
  if (!module)
    return NULL;

  import_array();

  return module;
}
