#pragma once

#include <fstream>
#include <string>
#include <vector>

#include "flock.hpp"
#include "particle.hpp"

struct OutputPaths {
  std::string staticPath;
  std::string dynamicPath;
};

class TrajectoryWriter {
 public:
  TrajectoryWriter(const OutputPaths& paths, const FlockParameters& parameters,
                   long steps, long saveEvery);

  void writeFrame(long step, const Particles& particles,
                  const std::vector<double>& angles);

 private:
  std::ofstream dynamic_;
};
