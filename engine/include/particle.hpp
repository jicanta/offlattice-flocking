#pragma once

#include <algorithm>
#include <vector>

struct Particle {
  double x = 0.0;
  double y = 0.0;
  double radius = 0.0;
  double property = 0.0;
};

using Particles = std::vector<Particle>;

inline double largestRadius(const Particles& particles) {
  double largest = 0.0;
  for (const Particle& particle : particles) {
    largest = std::max(largest, particle.radius);
  }
  return largest;
}
