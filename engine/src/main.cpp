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
      << "            [--dir <carpeta>] [--static ../data/static.txt]\n"
      << "            [--dynamic ../data/dynamic.txt]\n\n"
      << "  analyse   [--dir <carpeta>] [--static ../data/static.txt]\n"
      << "            [--dynamic ../data/dynamic.txt] [--out ../data/observables.txt]\n\n"
      << "  sweep     [--models vicsek,voter] [--rhos 2,4,8]\n"
      << "            [--etas 0:5:0.25] [--seeds 5] [--seed 1]\n"
      << "            [--steps 5000] [--jobs <hilos>] [--l 10] [--rc 1]\n"
      << "            [--v 0.03] [--dt 1] [--m <M>] [--voter-strict]\n"
      << "            [--dir ../data/sweep]\n\n"
      << "  bench     [--ns 100,200,400,800,1600,3200] [--ms <lista de M>]\n"
      << "            [--steps 200] [--repeats 3] [--no-brute] [--l 10]\n"
      << "            [--rc 1] [--eta 1.5] [--out ../data/bench.txt]\n\n"
      << "  simulate solo escribe estados (static.txt y dynamic.txt); los\n"
      << "  observables va y S se calculan despues con analyse, que lee esos\n"
      << "  archivos y escribe la serie \"t va S\". sweep hace lo mismo corrida\n"
      << "  por corrida (simula, analiza los estados y los borra) y guarda una\n"
      << "  serie temporal por corrida. --n tiene prioridad sobre --rho. --m\n"
      << "  por defecto usa el maximo admitido. --save-every ralea los cuadros\n"
      << "  de dynamic.txt. --voter-strict excluye a la particula del sorteo\n"
      << "  del modelo de votante.\n";
}

}  // namespace

int main(int argc, char** argv) {
  try {
    const Arguments arguments(argc, argv);
    if (arguments.command() == "simulate") {
      return runSimulate(arguments);
    }
    if (arguments.command() == "analyse") {
      return runAnalyse(arguments);
    }
    if (arguments.command() == "sweep") {
      return runSweep(arguments);
    }
    if (arguments.command() == "bench") {
      return runBench(arguments);
    }
    printUsage();
    return 1;
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << "\n";
    return 1;
  }
}
