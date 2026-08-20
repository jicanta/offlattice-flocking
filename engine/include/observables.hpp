#pragma once

#include <cmath>
#include <vector>

inline double polarization(const std::vector<double>& angles) {
  if (angles.empty()) {
    return 0.0;
  }
  double sine = 0.0;
  double cosine = 0.0;
  for (double angle : angles) {
    sine += std::sin(angle);
    cosine += std::cos(angle);
  }
  return std::hypot(sine, cosine) / static_cast<double>(angles.size());
}
