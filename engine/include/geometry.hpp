#pragma once

#include "particle.hpp"

inline constexpr int kOutside = -1;

struct Domain {
  double side = 0.0;
  bool periodic = false;

  double borderDistance(const Particle& first, const Particle& second) const;
  bool areNeighbors(const Particle& first, const Particle& second,
                    double interactionRadius) const;
};

int cellIndex(double coordinate, double cellSide, int cellsPerSide);

int shiftedIndexOrOutside(int index, int offset, int cellsPerSide,
                          bool periodic);
