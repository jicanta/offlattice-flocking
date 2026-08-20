#pragma once

#include <random>
#include <string>
#include <vector>

#include "geometry.hpp"
#include "neighbor_search.hpp"
#include "particle.hpp"

enum class Model { Vicsek, Voter };

Model modelFromName(const std::string& name);
std::string modelName(Model model);

struct FlockParameters {
  double side = 10.0;
  int count = 0;
  double interactionRadius = 1.0;
  double speed = 0.03;
  double timeStep = 1.0;
  double noise = 0.0;
  Model model = Model::Vicsek;
  bool voterIncludesSelf = true;
  bool bruteForce = false;
  int cellsPerSide = 0;
  unsigned int seed = 1;
};

int particleCount(double density, double side);

inline double density(const FlockParameters& parameters) {
  return parameters.count / (parameters.side * parameters.side);
}

class Flock {
 public:
  explicit Flock(const FlockParameters& parameters);

  void advance();

  const Particles& particles() const { return particles_; }
  const std::vector<double>& angles() const { return angles_; }
  const NeighborList& neighbors() const { return neighbors_; }
  int cellsPerSide() const { return cellsPerSide_; }
  double neighborMilliseconds() const { return neighborMilliseconds_; }
  long searches() const { return searches_; }

 private:
  void searchNeighbors();
  double vicsekAngle(int index) const;
  double voterAngle(int index);

  FlockParameters parameters_;
  Domain domain_;
  int cellsPerSide_;
  Particles particles_;
  std::vector<double> angles_;
  std::vector<double> nextAngles_;
  NeighborList neighbors_;
  std::mt19937 generator_;
  std::uniform_real_distribution<double> noise_;
  double neighborMilliseconds_ = 0.0;
  long searches_ = 0;
};
