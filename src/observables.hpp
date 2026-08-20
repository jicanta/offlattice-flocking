#pragma once

#include <cmath>
#include <vector>

namespace flock {

// Parametro de orden de Vicsek: modulo de la velocidad media normalizada,
//
//   va = |sum_i v_i| / (N v),
//
// que con |v_i| = v se reduce al modulo del promedio de los versores direccion.
// Vale ~0 con direcciones al azar y ~1 con las particulas polarizadas.
inline double polarization(const std::vector<double>& angles) {
    if (angles.empty()) return 0.0;

    double sumCos = 0.0;
    double sumSin = 0.0;
    for (const double theta : angles) {
        sumCos += std::cos(theta);
        sumSin += std::sin(theta);
    }
    return std::hypot(sumCos, sumSin) / static_cast<double>(angles.size());
}

}  // namespace flock
