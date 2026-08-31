#include "io.hpp"

#include <iomanip>
#include <stdexcept>

namespace {

std::ofstream openForWriting(const std::string& path) {
  std::ofstream stream(path);
  if (!stream) {
    throw std::invalid_argument("no se pudo abrir para escritura: " + path);
  }
  stream << std::setprecision(10);
  return stream;
}

}  // namespace

TrajectoryWriter::TrajectoryWriter(const OutputPaths& paths,
                                   const FlockParameters& parameters,
                                   long steps, long saveEvery) {
  std::ofstream staticStream = openForWriting(paths.staticPath);
  staticStream << "model " << modelName(parameters.model) << "\n"
               << "N " << parameters.count << "\n"
               << "L " << parameters.side << "\n"
               << "rho " << density(parameters) << "\n"
               << "rc " << parameters.interactionRadius << "\n"
               << "v " << parameters.speed << "\n"
               << "dt " << parameters.timeStep << "\n"
               << "eta " << parameters.noise << "\n"
               << "steps " << steps << "\n"
               << "save_every " << saveEvery << "\n"
               << "seed " << parameters.seed << "\n";

  dynamic_ = openForWriting(paths.dynamicPath);
}

void TrajectoryWriter::writeFrame(long step, const Particles& particles,
                                  const std::vector<double>& angles) {
  dynamic_ << step << "\n";
  for (std::size_t index = 0; index < particles.size(); ++index) {
    dynamic_ << particles[index].x << " " << particles[index].y << " "
             << angles[index] << "\n";
  }
}
