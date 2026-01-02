#ifndef COUPLED_ALPHA_COUPLED_ALPHA
#define COUPLED_ALPHA_COUPLED_ALPHA

#include <vector>
#include <cstdint>

#include "common.hpp"
#include "simplex.hpp"
#include "min_circumsphere.hpp"
#include "lifted_delaunay.hpp"

namespace coupled_alpha {

template<int D>
class CoupledAlpha {
 public:
  CoupledAlpha(
      const std::vector<Vectord<D>>& coords,
      const std::vector<uint8_t>& levels):
      coords_(coords), levels_(levels) {}
  
  std::array<std::unordered_map<Simplex, double, SimplexHash>, D + 2> compute() {
    LiftedDelaunay<D> ldelaunay;
    for (size_t i = 0; i < coords_.size(); ++i)
      ldelaunay.insert(coords_[i], levels_[i]);

    
    const auto cells = ldelaunay.cells();
    const auto simplices = CellsToSimpices<D>::compute(cells);

    for (int d = 0; d <= D + 1; ++d) {
      for (const auto& simplex: simplices[d]) {
        auto [sx, sy] = simplex.split(levels_);
        rfvs_[d][simplex] = RelaxedFiltrationValue<D>::compute(sx, sy, coords_);
      }
    }

    std::array<std::unordered_map<Simplex, double, SimplexHash>, D + 2> filtration_values;

    for (int d = D + 1; d >= 1; --d) {
      for (const auto& simplex: simplices[d]) {
        if (filtration_values[d].count(simplex) == 0) {
          filtration_values[d][simplex] = rfvs_[d][simplex].r;
        }

        double rs = filtration_values[d][simplex];
        
        for (const auto& face: simplex.faces()) {
          if (filtration_values[d - 1].count(face) == 1) {
            filtration_values[d - 1][face] = std::min(filtration_values[d - 1][face], rs);
          } else {
            if (!is_coupled_gabriel(face, simplex))
              filtration_values[d - 1][face] = rs;
          }
        }
      }
    }

    for (const auto& s: simplices[0])
      filtration_values[0][s] = 0.0;
    
    return filtration_values;
  }
  
  bool is_coupled_gabriel(const Simplex& face, const Simplex& simplex) {
    const auto& rfv = rfvs_[face.dim()][face];
    auto [sx, sy] = simplex.split(levels_);

    for (const auto v: sx.vertices()) {
      if ((coords_[v] - rfv.center).squaredNorm() <= rfv.rx - EPS)
        return false;
    }
    for (const auto v: sy.vertices()) {
      if ((coords_[v] - rfv.center).squaredNorm() <= rfv.ry - EPS)
        return false;
    }
    
    return true;
  }
  
 private:
  const std::vector<Vectord<D>>& coords_;
  const std::vector<uint8_t>& levels_;
  std::array<std::unordered_map<Simplex, RelaxedFiltrationValue<D>, SimplexHash>, D + 2> rfvs_;
};

  
} //namespace coupled_alpha


#endif
