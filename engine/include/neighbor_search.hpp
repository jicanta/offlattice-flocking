#pragma once

#include <cstddef>
#include <vector>

#include "geometry.hpp"
#include "particle.hpp"

using NeighborList = std::vector<std::vector<int>>;

std::size_t pairCount(const NeighborList& neighbors);

int maxCellsPerSide(double side, double interactionRadius, double maxRadius);

NeighborList bruteForceNeighbors(const Particles& particles,
                                 const Domain& domain,
                                 double interactionRadius);

NeighborList cellIndexNeighbors(const Particles& particles,
                                const Domain& domain, int cellsPerSide,
                                double interactionRadius);
