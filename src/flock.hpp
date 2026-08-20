#pragma once

#include <cmath>
#include <random>
#include <vector>

#include "cell_index_method.hpp"
#include "config.hpp"
#include "vec2.hpp"

namespace flock {

// Lleva un angulo al intervalo [-pi, pi).
inline double wrapAngle(double theta) {
    constexpr double kTwoPi = 2.0 * M_PI;
    theta = std::fmod(theta + M_PI, kTwoPi);
    if (theta < 0.0) theta += kTwoPi;
    return theta - M_PI;
}

// Estado del sistema de agentes autopropulsados y su regla de evolucion.
//
// La actualizacion es sincronica: en cada paso se calculan los vecinos con las
// posiciones en t, de ahi salen los angulos en t+1, y las posiciones avanzan con
// la velocidad en t.
class Flock {
public:
    explicit Flock(const Config& config);

    void step();

    long long time() const { return time_; }
    const std::vector<Vec2>& positions() const { return positions_; }
    const std::vector<double>& angles() const { return angles_; }
    // Vecinos calculados en el ultimo paso; base para el analisis de clusters.
    const NeighborLists& neighbors() const { return neighbors_; }

    const CellIndexMethod& cim() const { return cim_; }

    // Tiempo acumulado en la busqueda de vecinos y cantidad de invocaciones,
    // para el estudio de performance del CIM.
    double neighborSeconds() const { return neighborSeconds_; }
    long long neighborCalls() const { return neighborCalls_; }

private:
    double vicsekAngle(int i) const;
    double voterAngle(int i);

    Config config_;
    PeriodicBox box_;
    CellIndexMethod cim_;

    std::vector<Vec2> positions_;
    std::vector<double> angles_;
    std::vector<double> nextAngles_;
    NeighborLists neighbors_;

    std::mt19937_64 rng_;
    std::uniform_real_distribution<double> noise_;

    long long time_ = 0;
    double neighborSeconds_ = 0.0;
    long long neighborCalls_ = 0;
};

}  // namespace flock
