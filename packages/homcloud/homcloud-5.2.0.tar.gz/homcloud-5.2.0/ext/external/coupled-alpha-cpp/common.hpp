#ifndef COUPLED_ALPHA_COMMON
#define COUPLED_ALPHA_COMMON

#pragma GCC diagnostic ignored "-Wmaybe-uninitialized"
#include <Eigen/Dense>
#pragma GCC diagnostic warning "-Wmaybe-uninitialized"

namespace coupled_alpha {

static const double EPS = 1e-10;

template<int D> using Vectord = Eigen::Vector<double, D>;

template<int D> using Cell = std::array<uint32_t, D + 2>;


} // namespace coupled_alpha

#endif
