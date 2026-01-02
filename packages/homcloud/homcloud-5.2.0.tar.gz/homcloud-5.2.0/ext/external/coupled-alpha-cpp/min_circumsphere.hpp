#ifndef COUPLED_ALPHA_MIN_CIRCUMSPHERE
#define COUPLED_ALPHA_MIN_CIRCUMSPHERE

#include "common.hpp"
#include "simplex.hpp"

namespace coupled_alpha {

// template<int D>
// Vectord<D>
// partial_lsqst_problem(
//     MatrixType& A,
//     VectorType& b,
//     const Simplex& simplex,
//     const std::vector<Vectord<D>>& coords) {
//   assert(!simplex.empty());

//   const auto& x0 = coords[simplex[0]];
//   double sqnorm_x0 = x0.squaredNorm();
  
//   for (int i = 1; i <= simplex.dim(); ++i) {
//     A.row(i - 1) = (coords[simplex[i]] - x0).transpose();
//     b[i - 1] = 0.5 * (coords[simplex[i]].squaredNorm() - sqnorm_x0);
//   }
  
//   return x0;
// }

template<int D>
std::pair<double, Vectord<D>>
min_circumsphere(const Simplex& simplex, const std::vector<Vectord<D>>& coords) {
  switch (simplex.dim()) {
    case 0:
      return {0.0, coords[simplex[0]]};
    case 1:
      {
        auto& x0 = coords[simplex[0]];
        auto& x1 = coords[simplex[1]];
        return {(x0 - x1).squaredNorm() / 4.0, (x0 + x1) / 2.0};
      }
    case 2:
    case 3:
      {
        Eigen::MatrixXd A(simplex.dim(), D);
        Eigen::VectorXd b(simplex.dim());

        const auto& x0 = coords[simplex[0]];
        double sqnorm_x0 = x0.squaredNorm();
  
        for (int i = 1; i <= simplex.dim(); ++i) {
          A.row(i - 1) = (coords[simplex[i]] - x0).transpose();
          b[i - 1] = 0.5 * (coords[simplex[i]].squaredNorm() - sqnorm_x0);
        }
        
        // const Vectord<D> r = A.colPivHouseholderQr().solve(b - A * x0);
        const Vectord<D> r = A.bdcSvd(Eigen::ComputeThinU | Eigen::ComputeThinV).solve(b - A * x0);
        return {r.squaredNorm(), x0 + r};
      }
    default:
      assert(0);
      return {0.0, Vectord<D>::Zero()};
  }
}

template<int D>
struct RelaxedFiltrationValue {
  Vectord<D> center;
  double r, rx, ry;

  static RelaxedFiltrationValue compute(const Simplex& sx, const Simplex& sy,
                                        const std::vector<Vectord<D>>& coords) {
    if (sx.empty()) {
      auto [r, c] = min_circumsphere<D>(sy, coords);
      return {c, r, -1.0, r};
    }
    if (sy.empty()) {
      auto [r, c] = min_circumsphere<D>(sx, coords);
      return {c, r, r, -1.0};
    }

    int M = sx.dim();
    int N = sy.dim();

    if (M == 0 && N == 0) {
      auto [r, c] = min_circumsphere<D>(Simplex{sx[0], sy[0]}, coords);
      return {c, r, r, r};
    }
    
    Eigen::MatrixXd Ap(M + N + 1, D);
    Eigen::VectorXd bp(M + N + 1);
    const auto& x0 = coords[sx[0]];
    const auto& y0 = coords[sy[0]];
    
    {
      auto Ax = Ap.block(0, 0, M, D);
      auto bx = bp.segment(0, M);
      double sqnorm_x0 = x0.squaredNorm();
  
      for (int i = 1; i <= sx.dim(); ++i) {
        Ax.row(i - 1) = (coords[sx[i]] - x0).transpose();
        bx[i - 1] = 0.5 * (coords[sx[i]].squaredNorm() - sqnorm_x0);
      }
    }
    {
      auto Ay = Ap.block(M, 0, N, D);
      auto by = bp.segment(M, N);
      double sqnorm_y0 = y0.squaredNorm();
  
      for (int i = 1; i <= sy.dim(); ++i) {
        Ay.row(i - 1) = (coords[sy[i]] - y0).transpose();
        by[i - 1] = 0.5 * (coords[sy[i]].squaredNorm() - sqnorm_y0);
      }
    }
    // const auto x0 = partial_lsqst_problem(Ax, bx, sx, coords);
    // const auto y0 = partial_lsqst_problem(Ay, by, sy, coords);
    
    auto A = Ap.block(0, 0, M + N, D);
    auto b = bp.segment(0, M + N);
      
    const Vectord<D> cx = A.bdcSvd(Eigen::ComputeThinU | Eigen::ComputeThinV).solve(b - A * x0) + x0;
    double rxx = (cx - x0).squaredNorm();
    double rxy = (cx - y0).squaredNorm();
    if (rxx >= rxy)
      return {cx, rxx, rxx, rxy};
    
    const Vectord<D> cy = A.bdcSvd(Eigen::ComputeThinU | Eigen::ComputeThinV).solve(b - A * y0) + y0;
    double ryx = (cy - x0).squaredNorm();
    double ryy = (cy - y0).squaredNorm();
    if (ryy >= ryx)
      return {cy, ryy, ryx, ryy};

    Ap.row(N + M) = (x0 - y0).transpose();
    bp[N + M] = 0.5 * (x0.squaredNorm() - y0.squaredNorm());
    const Vectord<D> d = Ap.bdcSvd(Eigen::ComputeThinU | Eigen::ComputeThinV).solve(bp - Ap * x0);
    double r = d.squaredNorm();
    return {d + x0, r, r, r};
  }
};

} // namespace coupled_alpha

#endif
