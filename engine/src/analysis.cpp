#include "analysis.hpp"

#include <fstream>
#include <iomanip>
#include <stdexcept>
#include <vector>

#include "geometry.hpp"
#include "neighbor_search.hpp"
#include "observables.hpp"
#include "particle.hpp"

long analyseTrajectory(const std::string& statesPath, const TrajectoryInfo& info,
                       const std::string& observablesPath) {
  if (info.count <= 0 || info.side <= 0.0 || info.interactionRadius <= 0.0) {
    throw std::invalid_argument("faltan N, L o rc para analizar " + statesPath);
  }
  std::ifstream states(statesPath);
  if (!states) {
    throw std::invalid_argument("no se pudo leer " + statesPath);
  }
  std::ofstream observables(observablesPath);
  if (!observables) {
    throw std::invalid_argument("no se pudo escribir " + observablesPath);
  }
  observables << std::setprecision(10);

  const Domain domain{info.side, true};
  const int cellsPerSide =
      maxCellsPerSide(info.side, info.interactionRadius, 0.0);
  Particles particles(static_cast<std::size_t>(info.count));
  std::vector<double> angles(static_cast<std::size_t>(info.count));

  long frames = 0;
  long step = 0;
  while (states >> step) {
    for (std::size_t index = 0; index < particles.size(); ++index) {
      if (!(states >> particles[index].x >> particles[index].y >>
            angles[index])) {
        throw std::invalid_argument("cuadro incompleto en " + statesPath);
      }
    }
    const NeighborList neighbors = cellIndexNeighbors(
        particles, domain, cellsPerSide, info.interactionRadius);
    observables << step << " " << polarization(angles) << " "
                << largestClusterFraction(neighbors) << "\n";
    ++frames;
  }
  return frames;
}
