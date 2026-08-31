#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

#include "analysis.hpp"
#include "commands.hpp"

namespace {

// static.txt: un "clave valor" por linea. Solo hacen falta N, L y rc; el resto
// de las claves describe la corrida y aca se ignora.
TrajectoryInfo readStatic(const std::string& path) {
  std::ifstream input(path);
  if (!input) {
    throw std::invalid_argument("no se pudo leer " + path);
  }
  TrajectoryInfo info;
  std::string line;
  while (std::getline(input, line)) {
    std::istringstream pieces(line);
    std::string key;
    if (!(pieces >> key)) {
      continue;
    }
    if (key == "N") {
      pieces >> info.count;
    } else if (key == "L") {
      pieces >> info.side;
    } else if (key == "rc") {
      pieces >> info.interactionRadius;
    }
  }
  return info;
}

}  // namespace

int runAnalyse(const Arguments& arguments) {
  std::string staticPath = arguments.text("static", "../data/static.txt");
  std::string statesPath = arguments.text("dynamic", "../data/dynamic.txt");
  std::string observablesPath =
      arguments.text("out", "../data/observables.txt");
  if (arguments.has("dir")) {
    const std::filesystem::path directory = arguments.text("dir", "");
    staticPath = (directory / "static.txt").string();
    statesPath = (directory / "dynamic.txt").string();
    observablesPath = (directory / "observables.txt").string();
  }

  const TrajectoryInfo info = readStatic(staticPath);
  const long frames = analyseTrajectory(statesPath, info, observablesPath);

  std::cout << "estados: " << statesPath << "\n"
            << "cuadros analizados: " << frames << "\n"
            << "observables: " << observablesPath << "\n";
  return 0;
}
