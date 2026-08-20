#include <exception>
#include <iostream>

#include "commands.hpp"

namespace {

void printUsage() {
  std::cerr
      << "uso: flock <comando> [opciones]\n\n"
      << "  simulate  [--model vicsek|voter] [--l 10] [--rho 4] [--n <N>]\n"
      << "            [--rc 1] [--v 0.03] [--dt 1] [--eta 0]\n"
      << "            [--steps 1000] [--save-every 1] [--seed 1]\n"
      << "            [--method cim|brute] [--m <M>] [--voter-strict]\n"
      << "            [--static ../data/static.txt] [--dynamic "
         "../data/dynamic.txt]\n"
      << "            [--out ../data/polarization.txt]\n\n"
      << "  --n tiene prioridad sobre --rho. --m por defecto usa el maximo\n"
      << "  admitido. --voter-strict excluye a la particula del sorteo del\n"
      << "  modelo de votante.\n";
}

}  // namespace

int main(int argc, char** argv) {
  try {
    const Arguments arguments(argc, argv);
    if (arguments.command() == "simulate") {
      return runSimulate(arguments);
    }
    printUsage();
    return 1;
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << "\n";
    return 1;
  }
}
