#pragma once

#include <algorithm>
#include <cmath>
#include <vector>

#include "neighbor_search.hpp"

// Polarizacion va: modulo de la velocidad media normalizado por la rapidez,
// que para rapidez comun a todas las particulas se reduce al promedio de los
// versores de direccion.
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

// Fraccion S de particulas en la componente conexa mas grande del grafo de
// vecinos: un cluster es un conjunto donde todo par esta unido por una cadena
// de saltos entre particulas a distancia menor que rc. El grafo ya viene con
// las condiciones periodicas aplicadas.
inline double largestClusterFraction(const NeighborList& neighbors) {
  const std::size_t count = neighbors.size();
  if (count == 0) {
    return 0.0;
  }
  std::vector<bool> visited(count, false);
  std::vector<int> pending;
  std::size_t largest = 0;
  for (std::size_t seed = 0; seed < count; ++seed) {
    if (visited[seed]) {
      continue;
    }
    std::size_t size = 0;
    visited[seed] = true;
    pending.push_back(static_cast<int>(seed));
    while (!pending.empty()) {
      const int current = pending.back();
      pending.pop_back();
      ++size;
      for (int neighbor : neighbors[current]) {
        if (!visited[neighbor]) {
          visited[neighbor] = true;
          pending.push_back(neighbor);
        }
      }
    }
    largest = std::max(largest, size);
  }
  return static_cast<double>(largest) / static_cast<double>(count);
}
