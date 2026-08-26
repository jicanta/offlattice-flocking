#include <filesystem>
#include <iostream>
#include <stdexcept>

#include "commands.hpp"
#include "flock.hpp"
#include "io.hpp"
#include "observables.hpp"

int runSimulate(const Arguments& arguments) {
  FlockParameters parameters;
  parameters.side = arguments.number("l", 10.0);
  parameters.count =
      arguments.has("n") ? arguments.requiredInteger("n")
                         : particleCount(arguments.number("rho", 4.0),
                                         parameters.side);
  parameters.interactionRadius = arguments.number("rc", 1.0);
  parameters.speed = arguments.number("v", 0.03);
  parameters.timeStep = arguments.number("dt", 1.0);
  parameters.noise = arguments.number("eta", 0.0);
  parameters.model = modelFromName(arguments.text("model", "vicsek"));
  parameters.voterIncludesSelf = !arguments.has("voter-strict");
  parameters.cellsPerSide = arguments.integer("m", 0);
  parameters.seed = static_cast<unsigned int>(arguments.integer("seed", 1));

  const std::string method = arguments.text("method", "cim");
  if (method != "cim" && method != "brute") {
    throw std::invalid_argument("metodo desconocido: " + method);
  }
  parameters.bruteForce = method == "brute";

  const long steps = arguments.integer("steps", 1000);
  const long saveEvery = arguments.integer("save-every", 1);
  if (steps < 0) {
    throw std::invalid_argument("los pasos no pueden ser negativos");
  }
  if (saveEvery <= 0) {
    throw std::invalid_argument("save-every debe ser mayor que cero");
  }

  // --dir agrupa los tres archivos de la corrida en una carpeta, que es como
  // los consume el modulo de animacion (data/runs/<caso>/).
  OutputPaths paths{arguments.text("static", "../data/static.txt"),
                    arguments.text("dynamic", "../data/dynamic.txt"),
                    arguments.text("out", "../data/observables.txt")};
  if (arguments.has("dir")) {
    const std::filesystem::path directory = arguments.text("dir", "");
    std::filesystem::create_directories(directory);
    paths = {(directory / "static.txt").string(),
             (directory / "dynamic.txt").string(),
             (directory / "observables.txt").string()};
  }

  Flock flock(parameters);
  TrajectoryWriter writer(paths, parameters, steps, saveEvery);
  writer.writeFrame(0, flock.particles(), flock.angles());
  writer.writeObservable(0, polarization(flock.angles()),
                         largestClusterFraction(flock.neighbors()));

  for (long step = 1; step <= steps; ++step) {
    flock.advance();
    writer.writeObservable(step, polarization(flock.angles()),
                           largestClusterFraction(flock.neighbors()));
    if (step % saveEvery == 0) {
      writer.writeFrame(step, flock.particles(), flock.angles());
    }
  }

  std::cout << "modelo: " << modelName(parameters.model) << "\n"
            << "N: " << parameters.count << "\n"
            << "L: " << parameters.side << "\n"
            << "rho: " << density(parameters) << "\n"
            << "rc: " << parameters.interactionRadius << "\n"
            << "eta: " << parameters.noise << "\n"
            << "metodo: " << method << "\n";
  if (!parameters.bruteForce) {
    std::cout << "M: " << flock.cellsPerSide() << " (maximo "
              << maxCellsPerSide(parameters.side, parameters.interactionRadius,
                                 0.0)
              << ")\n";
  }
  std::cout << "pasos: " << steps << "\n"
            << "va final: " << polarization(flock.angles()) << "\n"
            << "S final: " << largestClusterFraction(flock.neighbors()) << "\n"
            << "busqueda de vecinos: " << flock.neighborMilliseconds()
            << " ms en " << flock.searches() << " llamadas ("
            << flock.neighborMilliseconds() / flock.searches()
            << " ms por llamada)\n"
            << "estatico: " << paths.staticPath << "\n"
            << "dinamico: " << paths.dynamicPath << "\n"
            << "observable: " << paths.observablePath << "\n";
  return 0;
}
