#pragma once

#include <fstream>
#include <string>
#include <vector>

#include "config.hpp"
#include "vec2.hpp"

namespace flock {

// Escribe la salida de la simulacion como archivos de texto. El modulo de
// animacion y el de analisis se ejecutan despues, de forma independiente, con
// estos archivos como entrada.
//
//   static.txt        parametros de la corrida, un "clave valor" por linea
//   dynamic.txt       por cuadro: una linea con t y luego N lineas "x y theta"
//   polarization.txt  una linea "t va" por cuadro
class TrajectoryWriter {
public:
    explicit TrajectoryWriter(const Config& config);

    void writeFrame(long long t, const std::vector<Vec2>& positions,
                    const std::vector<double>& angles);
    void writeObservable(long long t, double polarization);

private:
    std::ofstream dynamic_;
    std::ofstream observable_;
};

}  // namespace flock
