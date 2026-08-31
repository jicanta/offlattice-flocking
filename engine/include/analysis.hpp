#pragma once

#include <string>

// Post-procesamiento: los observables no se calculan durante la simulacion.
// El motor escribe estados (el formato de dynamic.txt: una linea con el paso y
// despues una linea "x y theta" por particula) y esta etapa los lee de vuelta
// para escribir la serie temporal "t va S", un cuadro por linea. Lo usan el
// comando `flock analyse` (sobre una corrida ya guardada) y el barrido, que
// analiza cada corrida apenas termina de simularla.
struct TrajectoryInfo {
  int count = 0;
  double side = 0.0;
  double interactionRadius = 0.0;
};

// Devuelve la cantidad de cuadros analizados.
long analyseTrajectory(const std::string& statesPath, const TrajectoryInfo& info,
                       const std::string& observablesPath);
