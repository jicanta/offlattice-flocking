#include "flock.hpp"

#include <cmath>
#include <stdexcept>

#include "stopwatch.hpp"

namespace {

constexpr double kPi = 3.14159265358979323846;

FlockParameters checked(const FlockParameters& parameters) {
  if (parameters.side <= 0.0) {
    throw std::invalid_argument("L debe ser mayor que cero");
  }
  if (parameters.count <= 0) {
    throw std::invalid_argument("N debe ser mayor que cero");
  }
  if (parameters.interactionRadius <= 0.0) {
    throw std::invalid_argument("rc debe ser mayor que cero");
  }
  if (parameters.speed < 0.0) {
    throw std::invalid_argument("v no puede ser negativo");
  }
  if (parameters.timeStep <= 0.0) {
    throw std::invalid_argument("dt debe ser mayor que cero");
  }
  if (parameters.noise < 0.0) {
    throw std::invalid_argument("eta no puede ser negativo");
  }
  if (parameters.cellsPerSide < 0) {
    throw std::invalid_argument("M no puede ser negativo");
  }
  return parameters;
}

double wrapAngle(double angle) {
  const double shifted = std::fmod(angle + kPi, 2.0 * kPi);
  return shifted < 0.0 ? shifted + kPi : shifted - kPi;
}

double wrapCoordinate(double coordinate, double side) {
  const double shifted = std::fmod(coordinate, side);
  const double inside = shifted < 0.0 ? shifted + side : shifted;
  return inside < side ? inside : 0.0;
}

}  // namespace

Model modelFromName(const std::string& name) {
  if (name == "vicsek") {
    return Model::Vicsek;
  }
  if (name == "voter") {
    return Model::Voter;
  }
  throw std::invalid_argument("modelo desconocido: " + name);
}

std::string modelName(Model model) {
  return model == Model::Vicsek ? "vicsek" : "voter";
}

int particleCount(double density, double side) {
  if (density <= 0.0) {
    throw std::invalid_argument("rho debe ser mayor que cero");
  }
  return static_cast<int>(std::lround(density * side * side));
}

Flock::Flock(const FlockParameters& parameters)
    : parameters_(checked(parameters)),
      domain_{parameters_.side, true},
      cellsPerSide_(parameters_.cellsPerSide > 0
                        ? parameters_.cellsPerSide
                        : maxCellsPerSide(parameters_.side,
                                          parameters_.interactionRadius, 0.0)),
      particles_(static_cast<std::size_t>(parameters_.count)),
      angles_(static_cast<std::size_t>(parameters_.count)),
      nextAngles_(static_cast<std::size_t>(parameters_.count)),
      generator_(parameters_.seed),
      noise_(-parameters_.noise / 2.0, parameters_.noise / 2.0) {
  std::uniform_real_distribution<double> coordinate(0.0, parameters_.side);
  std::uniform_real_distribution<double> angle(-kPi, kPi);
  for (std::size_t index = 0; index < particles_.size(); ++index) {
    particles_[index].x = coordinate(generator_);
    particles_[index].y = coordinate(generator_);
    angles_[index] = angle(generator_);
  }
  searchNeighbors();
}

void Flock::searchNeighbors() {
  const Stopwatch stopwatch;
  neighbors_ = parameters_.bruteForce
                   ? bruteForceNeighbors(particles_, domain_,
                                         parameters_.interactionRadius)
                   : cellIndexNeighbors(particles_, domain_, cellsPerSide_,
                                        parameters_.interactionRadius);
  neighborMilliseconds_ += stopwatch.elapsedMilliseconds();
  ++searches_;
}

double Flock::vicsekAngle(int index) const {
  double sine = std::sin(angles_[index]);
  double cosine = std::cos(angles_[index]);
  for (int neighbor : neighbors_[index]) {
    sine += std::sin(angles_[neighbor]);
    cosine += std::cos(angles_[neighbor]);
  }
  return std::atan2(sine, cosine);
}

double Flock::voterAngle(int index) {
  const std::vector<int>& neighbors = neighbors_[index];
  const std::size_t candidates =
      neighbors.size() + (parameters_.voterIncludesSelf ? 1 : 0);
  if (candidates == 0) {
    return angles_[index];
  }
  std::uniform_int_distribution<std::size_t> choice(0, candidates - 1);
  const std::size_t picked = choice(generator_);
  return picked < neighbors.size() ? angles_[neighbors[picked]] : angles_[index];
}

void Flock::advance() {
  for (std::size_t index = 0; index < particles_.size(); ++index) {
    const int id = static_cast<int>(index);
    const double heading = parameters_.model == Model::Vicsek ? vicsekAngle(id)
                                                              : voterAngle(id);
    nextAngles_[index] = wrapAngle(heading + noise_(generator_));
  }

  const double displacement = parameters_.speed * parameters_.timeStep;
  for (std::size_t index = 0; index < particles_.size(); ++index) {
    Particle& particle = particles_[index];
    particle.x = wrapCoordinate(
        particle.x + displacement * std::cos(angles_[index]), parameters_.side);
    particle.y = wrapCoordinate(
        particle.y + displacement * std::sin(angles_[index]), parameters_.side);
  }

  angles_.swap(nextAngles_);
  searchNeighbors();
}
