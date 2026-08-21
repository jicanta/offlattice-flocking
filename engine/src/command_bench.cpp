#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "commands.hpp"
#include "flock.hpp"

namespace {

std::vector<std::string> splitCommas(const std::string& text) {
  std::vector<std::string> pieces;
  std::istringstream stream(text);
  std::string piece;
  while (std::getline(stream, piece, ',')) {
    if (!piece.empty()) {
      pieces.push_back(piece);
    }
  }
  return pieces;
}

int toInteger(const std::string& text) {
  std::size_t consumed = 0;
  const int parsed = std::stoi(text, &consumed);
  if (consumed != text.size()) {
    throw std::invalid_argument("no es un entero: " + text);
  }
  return parsed;
}

}  // namespace

// Mide el costo de la busqueda de vecinos para el ejercicio (g): tiempo por
// llamada en funcion de N y de M, con fuerza bruta como referencia. El
// cronometro es el mismo que usa Flock, de modo que solo entra la busqueda y
// no la integracion ni la escritura a disco.
int runBench(const Arguments& arguments) {
  FlockParameters base;
  base.side = arguments.number("l", 10.0);
  base.interactionRadius = arguments.number("rc", 1.0);
  base.speed = arguments.number("v", 0.03);
  base.timeStep = arguments.number("dt", 1.0);
  base.noise = arguments.number("eta", 1.5);
  base.model = modelFromName(arguments.text("model", "vicsek"));

  const long steps = arguments.integer("steps", 200);
  const int repeats = arguments.integer("repeats", 3);
  if (steps <= 0 || repeats <= 0) {
    throw std::invalid_argument("--steps y --repeats deben ser mayores que cero");
  }

  std::vector<int> counts;
  for (const std::string& piece :
       splitCommas(arguments.text("ns", "100,200,400,800,1600,3200"))) {
    counts.push_back(toInteger(piece));
  }

  const int maximumCells =
      maxCellsPerSide(base.side, base.interactionRadius, 0.0);
  std::vector<int> cellCounts;
  if (arguments.has("ms")) {
    for (const std::string& piece : splitCommas(arguments.text("ms", ""))) {
      cellCounts.push_back(toInteger(piece));
    }
  } else {
    cellCounts.push_back(maximumCells);
  }

  const std::filesystem::path path = arguments.text("out", "../data/bench.txt");
  std::filesystem::create_directories(path.parent_path());
  std::ofstream output(path);
  if (!output) {
    throw std::invalid_argument("no se pudo escribir " + path.string());
  }
  output << std::setprecision(10);
  output << "# method N M L rc steps repeat ms_total ms_per_search\n";

  const auto measure = [&](const std::string& method, int count, int cells,
                           int repeat) {
    FlockParameters parameters = base;
    parameters.count = count;
    parameters.cellsPerSide = cells;
    parameters.bruteForce = method == "brute";
    parameters.seed = static_cast<unsigned int>(repeat + 1);

    Flock flock(parameters);
    for (long step = 0; step < steps; ++step) {
      flock.advance();
    }
    const double total = flock.neighborMilliseconds();
    const double perSearch = total / static_cast<double>(flock.searches());
    output << method << " " << count << " "
           << (method == "brute" ? 0 : flock.cellsPerSide()) << " "
           << base.side << " " << base.interactionRadius << " " << steps << " "
           << repeat << " " << total << " " << perSearch << "\n";
    std::cout << method << " N=" << count
              << (method == "brute" ? std::string()
                                    : " M=" + std::to_string(flock.cellsPerSide()))
              << " repeticion " << repeat << ": " << perSearch
              << " ms por busqueda\n";
  };

  for (int count : counts) {
    for (int repeat = 0; repeat < repeats; ++repeat) {
      for (int cells : cellCounts) {
        if (cells > maximumCells) {
          throw std::invalid_argument(
              "M=" + std::to_string(cells) + " supera el maximo " +
              std::to_string(maximumCells));
        }
        measure("cim", count, cells, repeat);
      }
      if (!arguments.has("no-brute")) {
        measure("brute", count, 0, repeat);
      }
    }
  }

  std::cout << "salida: " << path.string() << "\n";
  return 0;
}
