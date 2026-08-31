#include <atomic>
#include <exception>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

#include "analysis.hpp"
#include "commands.hpp"
#include "flock.hpp"

namespace {

std::vector<std::string> split(const std::string& text, char separator) {
  std::vector<std::string> pieces;
  std::istringstream stream(text);
  std::string piece;
  while (std::getline(stream, piece, separator)) {
    if (!piece.empty()) {
      pieces.push_back(piece);
    }
  }
  return pieces;
}

double toNumber(const std::string& text) {
  std::size_t consumed = 0;
  const double parsed = std::stod(text, &consumed);
  if (consumed != text.size()) {
    throw std::invalid_argument("no es un numero: " + text);
  }
  return parsed;
}

// Acepta una lista "0,1,2.5" o un rango inclusivo "desde:hasta:paso".
std::vector<double> numberList(const std::string& text) {
  const std::vector<std::string> range = split(text, ':');
  if (range.size() == 3) {
    const double from = toNumber(range[0]);
    const double to = toNumber(range[1]);
    const double step = toNumber(range[2]);
    if (step <= 0.0 || to < from) {
      throw std::invalid_argument("rango invalido: " + text);
    }
    std::vector<double> values;
    const int count = static_cast<int>(std::lround((to - from) / step));
    for (int index = 0; index <= count; ++index) {
      values.push_back(from + step * index);
    }
    return values;
  }
  std::vector<double> values;
  for (const std::string& piece : split(text, ',')) {
    values.push_back(toNumber(piece));
  }
  if (values.empty()) {
    throw std::invalid_argument("lista vacia: " + text);
  }
  return values;
}

std::string shortNumber(double value) {
  std::ostringstream stream;
  stream << std::setprecision(6) << value;
  return stream.str();
}

struct Run {
  Model model;
  double density;
  double noise;
  unsigned int seed;
  std::string name;
};

}  // namespace

int runSweep(const Arguments& arguments) {
  FlockParameters base;
  base.side = arguments.number("l", 10.0);
  base.interactionRadius = arguments.number("rc", 1.0);
  base.speed = arguments.number("v", 0.03);
  base.timeStep = arguments.number("dt", 1.0);
  base.voterIncludesSelf = !arguments.has("voter-strict");
  base.cellsPerSide = arguments.integer("m", 0);

  const std::vector<std::string> models =
      split(arguments.text("models", "vicsek,voter"), ',');
  const std::vector<double> densities =
      numberList(arguments.text("rhos", "2,4,8"));
  const std::vector<double> noises =
      numberList(arguments.text("etas", "0:5:0.25"));
  const int seedCount = arguments.integer("seeds", 5);
  const unsigned int firstSeed =
      static_cast<unsigned int>(arguments.integer("seed", 1));
  const long steps = arguments.integer("steps", 5000);
  if (seedCount <= 0) {
    throw std::invalid_argument("--seeds debe ser mayor que cero");
  }
  if (steps <= 0) {
    throw std::invalid_argument("--steps debe ser mayor que cero");
  }

  const std::filesystem::path directory = arguments.text("dir", "../data/sweep");
  std::filesystem::create_directories(directory);

  std::vector<Run> runs;
  for (const std::string& model : models) {
    for (double density : densities) {
      for (double noise : noises) {
        for (int index = 0; index < seedCount; ++index) {
          const unsigned int seed = firstSeed + static_cast<unsigned int>(index);
          runs.push_back({modelFromName(model), density, noise, seed,
                          model + "_rho" + shortNumber(density) + "_eta" +
                              shortNumber(noise) + "_seed" +
                              std::to_string(seed) + ".txt"});
        }
      }
    }
  }

  const unsigned int available = std::thread::hardware_concurrency();
  const int jobs = arguments.integer(
      "jobs", static_cast<int>(available > 0 ? available : 1));
  if (jobs <= 0) {
    throw std::invalid_argument("--jobs debe ser mayor que cero");
  }

  std::cout << "corridas: " << runs.size() << " (" << models.size()
            << " modelos x " << densities.size() << " densidades x "
            << noises.size() << " ruidos x " << seedCount << " semillas)\n"
            << "pasos por corrida: " << steps << "\n"
            << "hilos: " << jobs << "\n"
            << "salida: " << directory.string() << "\n";

  std::atomic<std::size_t> next{0};
  std::atomic<std::size_t> done{0};
  std::mutex console;

  // Una excepcion que escapa del cuerpo de un std::thread llama a
  // std::terminate y aborta el barrido sin explicar por que. Se guarda la
  // primera que aparezca, se corta el reparto de trabajo y se relanza en el
  // hilo principal despues del join.
  std::atomic<bool> failed{false};
  std::exception_ptr failure;
  std::mutex failureGuard;

  const auto worker = [&]() {
   try {
    for (std::size_t index = next++; index < runs.size() && !failed;
         index = next++) {
      const Run& run = runs[index];
      FlockParameters parameters = base;
      parameters.model = run.model;
      parameters.count = particleCount(run.density, parameters.side);
      parameters.noise = run.noise;
      parameters.seed = run.seed;

      // La simulacion solo escribe estados; los observables se calculan
      // despues, leyendo ese archivo, igual que con `flock analyse`. Guardar
      // los estados de todas las corridas ocuparia cientos de gigabytes, asi
      // que cada corrida se analiza apenas termina y su archivo de estados se
      // borra. Se escriben con 17 cifras (max_digits10) para que el double
      // que se relee sea exactamente el simulado.
      const std::filesystem::path statesPath =
          directory / (run.name + ".estados");
      {
        std::ofstream states(statesPath);
        if (!states) {
          throw std::invalid_argument("no se pudo escribir " +
                                      statesPath.string());
        }
        states << std::setprecision(17);
        Flock flock(parameters);
        const auto writeFrame = [&](long step) {
          states << step << "\n";
          for (std::size_t index = 0; index < flock.particles().size();
               ++index) {
            states << flock.particles()[index].x << " "
                   << flock.particles()[index].y << " "
                   << flock.angles()[index] << "\n";
          }
        };
        writeFrame(0);
        for (long step = 1; step <= steps; ++step) {
          flock.advance();
          writeFrame(step);
        }
      }

      const TrajectoryInfo info{parameters.count, parameters.side,
                                parameters.interactionRadius};
      analyseTrajectory(statesPath.string(), info,
                        (directory / run.name).string());
      std::filesystem::remove(statesPath);

      const std::size_t finished = ++done;
      if (finished % 10 == 0 || finished == runs.size()) {
        const std::lock_guard<std::mutex> lock(console);
        std::cout << finished << "/" << runs.size() << "\r" << std::flush;
      }
    }
   } catch (...) {
     const std::lock_guard<std::mutex> lock(failureGuard);
     if (!failure) {
       failure = std::current_exception();
     }
     failed = true;
   }
  };

  std::vector<std::thread> pool;
  for (int index = 0; index < jobs; ++index) {
    pool.emplace_back(worker);
  }
  for (std::thread& thread : pool) {
    thread.join();
  }
  std::cout << "\n";
  if (failure) {
    std::rethrow_exception(failure);
  }

  std::ofstream index(directory / "index.txt");
  if (!index) {
    throw std::invalid_argument("no se pudo escribir index.txt");
  }
  index << "# model rho N eta seed steps L rc v dt file\n";
  for (const Run& run : runs) {
    index << modelName(run.model) << " " << shortNumber(run.density) << " "
          << particleCount(run.density, base.side) << " "
          << shortNumber(run.noise) << " " << run.seed << " " << steps << " "
          << base.side << " " << base.interactionRadius << " " << base.speed
          << " " << base.timeStep << " " << run.name << "\n";
  }

  std::cout << "indice: " << (directory / "index.txt").string() << "\n";
  return 0;
}
