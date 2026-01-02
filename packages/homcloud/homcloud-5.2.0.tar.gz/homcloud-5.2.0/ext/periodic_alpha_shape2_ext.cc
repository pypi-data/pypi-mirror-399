#include "homcloud_common.h"
#include "homcloud_cgal.h"
#include "homcloud_numpy.h"
#include "alpha_shape_ext_common.h"

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

#include <CGAL/Periodic_2_Delaunay_triangulation_traits_2.h>
#include <CGAL/Periodic_2_Delaunay_triangulation_2.h>
 
#include <CGAL/Alpha_shape_2.h>
#include <CGAL/Alpha_shape_face_base_2.h>
#include <CGAL/Alpha_shape_vertex_base_2.h>
#include <CGAL/Triangulation_vertex_base_with_info_2.h>

struct VertexInfo {
  int index;
};

// Traits
typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel;
typedef CGAL::Periodic_2_Delaunay_triangulation_traits_2<Kernel> Gt;

// Vertex types
typedef CGAL::Periodic_2_triangulation_vertex_base_2<Gt> Vb;
typedef CGAL::Triangulation_vertex_base_with_info_2<VertexInfo, Gt, Vb> Vinfo;
typedef CGAL::Alpha_shape_vertex_base_2<Gt, Vinfo> AsVb;

// Cell types
typedef CGAL::Periodic_2_triangulation_face_base_2<Gt> Cb;
typedef CGAL::Alpha_shape_face_base_2<Gt, Cb> AsCb;

typedef CGAL::Triangulation_data_structure_2<AsVb, AsCb> Tds;
typedef CGAL::Periodic_2_Delaunay_triangulation_2<Gt, Tds> P2DT2;
typedef CGAL::Alpha_shape_2<P2DT2> PeriodicAlphaShape2;

using Point = Gt::Point_2;
using Vertex_handle = PeriodicAlphaShape2::Vertex_handle;
using Edge_iterator = PeriodicAlphaShape2::Edge_iterator;
using Face_handle = PeriodicAlphaShape2::Face_handle;
using PointWithInfo = std::pair<Point, VertexInfo>;

static std::vector<PointWithInfo> BuildPointCloud(PyArrayObject* array) {
  std::vector<PointWithInfo> points;
  int npoints = PyArray_DIMS(array)[0];

  for (int i = 0; i < npoints; ++i) {
    double x = *GETPTR2D<double>(array, i, 0);
    double y = *GETPTR2D<double>(array, i, 1);
    points.emplace_back(Point(x, y), VertexInfo{i});
  }
  return points;
}

static bool IsDomainValidShape(double xmin, double  xmax, double ymin, double ymax) {
  if (!((xmin < xmax) && (ymin < ymax))) {
    PyErr_SetString(PyExc_ValueError, "Periodic region invalid");
    return false;
  }
  
  double ratio = (xmax - xmin) / (ymax - ymin);
  if (ratio > 1.6 || ratio < 1 / 1.6) {
    PyErr_SetString(PyExc_ValueError, "Too anistropic periodic region is invalid (1.6)");
    return false;
  }
  
  return true;
}

static bool IsPointsInDomain(const std::vector<PointWithInfo>& points, const P2DT2::Iso_rectangle& domain) {
  for (const auto& point_info_pair: points) {
    double x = point_info_pair.first[0];
    double y = point_info_pair.first[1];
    if (!(domain.xmin() <= x && x <= domain.xmax() && domain.ymin() <= y && y <= domain.ymax()))
      return false;
  }
  return true;
}

static bool IsFaceOverlapping(Face_handle h) {
  std::array<int, 3> vertices = {
    h->vertex(0)->info().index,
    h->vertex(1)->info().index,
    h->vertex(2)->info().index,
  };

  std::sort(vertices.begin(), vertices.end());
  return (vertices[0] == vertices[1]) || (vertices[1] == vertices[2]);
}

static bool HasAlphaShapeOverlappingFace(const PeriodicAlphaShape2& alpha_shape) {
  for (auto it = alpha_shape.faces_begin(); it != alpha_shape.faces_end(); ++it) {
    if (IsFaceOverlapping(it)) {
      return true;
    }
  }
  return false;
}

static int NumSimplices(const PeriodicAlphaShape2& alpha_shape) {
  return alpha_shape.number_of_vertices() +
    std::distance(alpha_shape.finite_edges_begin(), alpha_shape.finite_edges_end()) +
    alpha_shape.number_of_faces();
}

static PyObject* CreateSimplexAlphaPairForVertex(Vertex_handle h) {
  return Py_BuildValue("((i)d)", h->info().index, 0.0);
}

static PyObject* CreateSimplexAlphaPairForEdge(const PeriodicAlphaShape2& alpha_shape, Edge_iterator it) {
  int v1 = it->first->vertex((it->second + 1) % 3)->info().index;
  int v2 = it->first->vertex((it->second + 2) % 3)->info().index;
  int w1 = std::min(v1, v2);
  int w2 = std::max(v1, v2);
  double a1 = it->first->get_ranges(it->second).get<0>();
  double a2 = it->first->get_ranges(it->second).get<1>();
  double a = (a1 > 0) ? a1 : a2;
  
  return Py_BuildValue("((ii)d)", w1, w2, a);
}

static PyObject* CreateSimplexAlphaPairForFace(const PeriodicAlphaShape2& alpha_shape, Face_handle it) {
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
  double xmin, xmax, ymin, ymax;
  
  if (!PyArg_ParseTuple(args, "O!pdddd", &PyArray_Type, &array, &weighted, &xmin, &xmax, &ymin, &ymax))
    return NULL;

  if (weighted) {
     PyErr_SetString(PyExc_ValueError, "2D Periodic alpha shape does not accept weighted points");
     return NULL;
  }

  if (!IsArrayValidPointCloud(array, 2, 0))
    return NULL;

  if (!IsDomainValidShape(xmin, xmax, ymin, ymax))
    return NULL;
  
  std::vector<PointWithInfo> points = BuildPointCloud(array);
  P2DT2::Iso_rectangle domain(xmin, ymin, xmax, ymax);
  
  if (!IsPointsInDomain(points, domain)) {
    PyErr_SetString(PyExc_ValueError, "Point out of the unit cell");
    return NULL;
  }
  
  P2DT2 triangulation(points.begin(), points.end(), domain);

  if (triangulation.is_triangulation_in_1_sheet()) {
    triangulation.convert_to_1_sheeted_covering();
  } else {
    PyErr_SetString(PyExc_ValueError, "Points are too few for periodic 2D alpha shape. 1-sheet covering is not allowed");
    return NULL;
  }
  
  PeriodicAlphaShape2 alpha_shape(triangulation, 0, PeriodicAlphaShape2::GENERAL);

  if (HasAlphaShapeOverlappingFace(alpha_shape)) {
     PyErr_SetString(PyExc_ValueError, "Periodic 2D Alpha Shape has an overlapping face");
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

  for (auto it = alpha_shape.faces_begin(); it != alpha_shape.faces_end(); ++it, ++i) {
    PyObject* pair = CreateSimplexAlphaPairForFace(alpha_shape, it);
    if (!pair) goto error;
    PyList_SetItem(simplex_alpha_pairs, i, pair);
  }

  return simplex_alpha_pairs;
error:
  Py_XDECREF(simplex_alpha_pairs);
  return NULL;
}

static PyMethodDef periodic_alpha_shape2_ext_functions[] = {
  {"compute", (PyCFunction)compute, METH_VARARGS, "Compute a Periodic 2D alpha shape"},
  {NULL, NULL, 0, NULL}
};
  
static PyModuleDef periodic_alpha_shape2_ext_module = {
  PyModuleDef_HEAD_INIT,
  "homcloud.periodic_alpha_shape2_ext",
  "The C++ module for Periodic 2D Alpha shape",
  -1,
  periodic_alpha_shape2_ext_functions
};

PyMODINIT_FUNC
PyInit_periodic_alpha_shape2_ext() {
  PyObject* module = PyModule_Create(&periodic_alpha_shape2_ext_module);
  if (!module)
    return NULL;

  import_array();

  return module;
}
