#include "geometry.hpp"

#include <cmath>

namespace {

double minimumImageDelta(double from, double to, const Domain& domain) {
  const double delta = to - from;
  if (!domain.periodic) {
    return delta;
  }
  if (delta > domain.side / 2.0) {
    return delta - domain.side;
  }
  if (delta < -domain.side / 2.0) {
    return delta + domain.side;
  }
  return delta;
}

double squaredCenterDistance(const Domain& domain, const Particle& first,
                             const Particle& second) {
  const double deltaX = minimumImageDelta(first.x, second.x, domain);
  const double deltaY = minimumImageDelta(first.y, second.y, domain);
  return deltaX * deltaX + deltaY * deltaY;
}

}  // namespace

double Domain::borderDistance(const Particle& first,
                              const Particle& second) const {
  return std::sqrt(squaredCenterDistance(*this, first, second)) - first.radius -
         second.radius;
}

bool Domain::areNeighbors(const Particle& first, const Particle& second,
                          double interactionRadius) const {
  const double reach = interactionRadius + first.radius + second.radius;
  return squaredCenterDistance(*this, first, second) < reach * reach;
}

int cellIndex(double coordinate, double cellSide, int cellsPerSide) {
  const int index = static_cast<int>(coordinate / cellSide);
  if (index < 0) {
    return 0;
  }
  return index < cellsPerSide ? index : cellsPerSide - 1;
}

int shiftedIndexOrOutside(int index, int offset, int cellsPerSide,
                          bool periodic) {
  const int shifted = index + offset;
  if (shifted >= 0 && shifted < cellsPerSide) {
    return shifted;
  }
  return periodic ? (shifted + cellsPerSide) % cellsPerSide : kOutside;
}
