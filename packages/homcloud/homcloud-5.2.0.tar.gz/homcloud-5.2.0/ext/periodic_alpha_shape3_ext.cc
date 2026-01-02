#include "homcloud_common.h"
#include "homcloud_cgal.h"
#include "homcloud_numpy.h"
#include "alpha_shape_ext_common.h"

#include <CGAL/Periodic_3_regular_triangulation_traits_3.h>
#include <CGAL/Periodic_3_regular_triangulation_3.h>
#include <CGAL/Triangulation_vertex_base_with_info_3.h>
#include <CGAL/Alpha_shape_3.h>
#include <CGAL/Alpha_shape_cell_base_3.h>
#include <CGAL/Alpha_shape_vertex_base_3.h>

struct VertexInfo {
  int index;
};

// Kernels and traits
using K = CGAL::Exact_predicates_inexact_constructions_kernel;
using Gt = CGAL::Periodic_3_regular_triangulation_traits_3<K>;

// Vertex classes hierarchy
using P3DsVb = CGAL::Periodic_3_triangulation_ds_vertex_base_3<>;
using RtVb = CGAL::Regular_triangulation_vertex_base_3<Gt, P3DsVb>;
using InfoVb = CGAL::Triangulation_vertex_base_with_info_3<VertexInfo, Gt, RtVb>;
using AsVb = CGAL::Alpha_shape_vertex_base_3<Gt, InfoVb>;


// Cell classes hierarchy
using P3DsCb = CGAL::Periodic_3_triangulation_ds_cell_base_3<>;
using RtCb = CGAL::Regular_triangulation_cell_base_3<Gt, P3DsCb>;
using AsCb = CGAL::Alpha_shape_cell_base_3<Gt,RtCb>;

// Triangulation class and Alpha shape
using TDS = CGAL::Triangulation_data_structure_3<AsVb, AsCb>;
using P3Rt = CGAL::Periodic_3_regular_triangulation_3<Gt, TDS>;
using PeriodicAlphaShape3 = CGAL::Alpha_shape_3<P3Rt>;

// Types
using Bare_point = P3Rt::Bare_point;
using Weighted_point = P3Rt::Weighted_point;
using Iso_cuboid = P3Rt::Iso_cuboid;
using Vertex_handle = PeriodicAlphaShape3::Vertex_handle;
using Edge_iterator = PeriodicAlphaShape3::Edge_iterator;
using Facet_iterator = PeriodicAlphaShape3::Facet_iterator;
using Cell_handle = PeriodicAlphaShape3::Cell_handle;

static std::vector<Weighted_point> BuildPointCloud(PyArrayObject* array, int weighted) {
  std::vector<Weighted_point> points;
  int npoints = PyArray_DIMS(array)[0];

  for (int i = 0; i < npoints; ++i) {
    double x = *GETPTR2D<double>(array, i, 0);
    double y = *GETPTR2D<double>(array, i, 1);
    double z = *GETPTR2D<double>(array, i, 2);
    double w = weighted ? *GETPTR2D<double>(array, i, 3) : 0.0;
    points.emplace_back(Bare_point(x, y, z), w);
  }
  return points;
}

static std::map<Bare_point, int> BuildPointToIndexMap(const std::vector<Weighted_point>& points) {
  std::map<Bare_point, int> point2index;
  
  for (size_t i = 0; i < points.size(); ++i) {
    point2index.insert(std::make_pair(points[i], i));
  }

  return point2index;
}

static bool IsDomainValidShape(double xmin, double  xmax, double ymin, double ymax, double zmin, double zmax) {
#if (CGAL_VERSION_NR < 1050601000)
  if (xmax - xmin != ymax - ymin || xmax - xmin != zmax - zmin) {
    PyErr_SetString(PyExc_ValueError, "Noncubic rectangular periodic condition is only supported CGAL >= 5.6.");
    return false;
  }
#endif
  if ((xmin >= xmax) || (ymin >= ymax) || (zmin >= zmax)) {
    PyErr_SetString(PyExc_ValueError, "Unit cell coordinate is invalid");
    return false;
  }
  return true;
}

static Py_ssize_t NumSimplices(const PeriodicAlphaShape3& alpha_shape) {
  return (alpha_shape.number_of_vertices() +
          alpha_shape.number_of_edges() +
          alpha_shape.number_of_facets() +
          alpha_shape.number_of_cells());
}

static double AlphaValue(const CGAL::Alpha_status<double>& status) {
  return status.is_Gabriel() ? status.alpha_min() : status.alpha_mid();
}

static bool IsCellOverlapping(Cell_handle h) {
  std::array<int, 4> vertices = {
    h->vertex(0)->info().index,
    h->vertex(1)->info().index,
    h->vertex(2)->info().index,
    h->vertex(3)->info().index,
  };

  std::sort(vertices.begin(), vertices.end());
  return (vertices[0] == vertices[1]) || (vertices[1] == vertices[2]) || (vertices[2] == vertices[3]);
}

static bool HasAlphaShapeOverlappingCell(const PeriodicAlphaShape3& alpha_shape) {
  for (auto it = alpha_shape.cells_begin(); it != alpha_shape.cells_end(); ++it) {
    if (IsCellOverlapping(it)) {
      return true;
    }
  }
  return false;
}

static PyObject* CreateSimplexAlphaPairForVertex(Vertex_handle h) {
  return Py_BuildValue("((i)d)", h->info().index, -(h->point().weight()));
}

static PyObject* CreateSimplexAlphaPairForEdge(const PeriodicAlphaShape3& alpha_shape, Edge_iterator it) {
  int v1 = it->first->vertex(it->second)->info().index;
  int v2 = it->first->vertex(it->third)->info().index;
  int w1 = std::min(v1, v2);
  int w2 = std::max(v1, v2);
  double a = AlphaValue(alpha_shape.get_alpha_status(*it));
  
  return Py_BuildValue("((ii)d)", w1, w2, a);
}

static PyObject* CreateSimplexAlphaPairForFacet(const PeriodicAlphaShape3& alpha_shape, Facet_iterator it) {
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

static PyObject* CreateSimplexAlphaPairForCell(const PeriodicAlphaShape3& alpha_shape, Cell_handle it) {
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
  double xmin;
  double xmax;
  double ymin;
  double ymax;
  double zmin;
  double zmax;
  
  if (!PyArg_ParseTuple(args, "O!pdddddd", &PyArray_Type, &array, &weighted, &xmin, &xmax, &ymin, &ymax, &zmin, &zmax))
    return NULL;

  if (!(IsArrayValidPointCloud(array, 3, weighted)))
    return NULL;

  if (!IsDomainValidShape(xmin, xmax, ymin, ymax, zmin, zmax))
    return NULL;

  std::vector<Weighted_point> points = BuildPointCloud(array, weighted);
  Iso_cuboid domain(xmin, ymin, zmin, xmax, ymax, zmax);
  P3Rt triangulation(points.begin(), points.end(), domain);
  
  if (triangulation.is_triangulation_in_1_sheet()) {
    triangulation.convert_to_1_sheeted_covering();
  } else {
    PyErr_SetString(PyExc_ValueError, "Points are too few for periodic 3D alpha shape. 1-sheet covering is not allowed");
    return NULL;
  }

  PeriodicAlphaShape3 alpha_shape(triangulation, 0, PeriodicAlphaShape3::GENERAL);

  std::map<Bare_point, int> point2index = BuildPointToIndexMap(points);

  for (auto it = alpha_shape.unique_vertices_begin(); it != alpha_shape.unique_vertices_end(); ++it) {
    it->info().index = point2index[it->point().point()];
  }

  if (HasAlphaShapeOverlappingCell(alpha_shape)) {
     PyErr_SetString(PyExc_ValueError, "PeriodicAlphaShape3 has an overlapping cell");
     return NULL;
  }
  
  PyObject* simplex_alpha_pairs = PyList_New(NumSimplices(alpha_shape));
  if (!simplex_alpha_pairs) goto error;

  int i;

  i = 0;
  for (auto it = alpha_shape.unique_vertices_begin(); it != alpha_shape.unique_vertices_end(); ++it, ++i) {
    PyObject* pair = CreateSimplexAlphaPairForVertex(it);
    if (!pair) goto error;
    PyList_SetItem(simplex_alpha_pairs, i, pair);
  }

  for (auto it = alpha_shape.edges_begin(); it != alpha_shape.edges_end(); ++it, ++i) {
    PyObject* pair = CreateSimplexAlphaPairForEdge(alpha_shape, it);
    if (!pair) goto error;
    PyList_SetItem(simplex_alpha_pairs, i, pair);
  }

  for (auto it = alpha_shape.facets_begin(); it != alpha_shape.facets_end(); ++it, ++i) {
    PyObject* pair = CreateSimplexAlphaPairForFacet(alpha_shape, it);
    if (!pair) goto error;
    PyList_SetItem(simplex_alpha_pairs, i, pair);
  }

  for (auto it = alpha_shape.cells_begin(); it != alpha_shape.cells_end(); ++it, ++i) {
    PyObject* pair = CreateSimplexAlphaPairForCell(alpha_shape, it);
    if (!pair) goto error;
    PyList_SetItem(simplex_alpha_pairs, i, pair);
  }

  return simplex_alpha_pairs;
  
error:
  Py_XDECREF(simplex_alpha_pairs);
  return NULL;
  
}

static PyMethodDef periodic_alpha_shape3_ext_functions[] = {
  {"compute", (PyCFunction)compute, METH_VARARGS, "Compute a Periodic 3D alpha shape"},
  {NULL, NULL, 0, NULL}
};
  
static PyModuleDef periodic_alpha_shape3_ext_module = {
  PyModuleDef_HEAD_INIT,
  "homcloud.periodic_alpha_shape3_ext",
  "The C++ module for Periodic 3D Alpha shape",
  -1,
  periodic_alpha_shape3_ext_functions
};

PyMODINIT_FUNC
PyInit_periodic_alpha_shape3_ext() {
  PyObject* module = PyModule_Create(&periodic_alpha_shape3_ext_module);
  if (!module)
    return NULL;

  import_array();

  return module;
}
