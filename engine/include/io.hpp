#pragma once

#include <fstream>
#include <string>
#include <vector>

#include "flock.hpp"
#include "particle.hpp"

struct OutputPaths {
  std::string staticPath;
  std::string dynamicPath;
  std::string observablePath;
};

class TrajectoryWriter {
 public:
  TrajectoryWriter(const OutputPaths& paths, const FlockParameters& parameters,
                   long steps, long saveEvery);

  void writeFrame(long step, const Particles& particles,
                  const std::vector<double>& angles);
  void writeObservable(long step, double value);

 private:
  std::ofstream dynamic_;
  std::ofstream observable_;
};
