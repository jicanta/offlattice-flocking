#include "flock.hpp"

#include <chrono>

namespace flock {

Flock::Flock(const Config& config)
    : config_(config),
      box_(config.L),
      cim_(box_, config.rc, config.cellsPerSide),
      rng_(config.seed),
      noise_(-config.eta / 2.0, config.eta / 2.0) {
    // Condicion inicial: N particulas uniformes en la caja, con el mismo modulo
    // de velocidad y direcciones uniformes en [-pi, pi).
    std::uniform_real_distribution<double> position(0.0, config.L);
    std::uniform_real_distribution<double> angle(-M_PI, M_PI);

    positions_.reserve(config.N);
    angles_.reserve(config.N);
    for (int i = 0; i < config.N; ++i) {
        positions_.push_back({position(rng_), position(rng_)});
        angles_.push_back(angle(rng_));
    }
    nextAngles_.assign(config.N, 0.0);
    neighbors_.resize(config.N);

    // Los vecinos del estado inicial quedan disponibles antes del primer paso.
    cim_.computeNeighbors(positions_, neighbors_);
}

// Modelo estandar: promedio vectorial de las direcciones del entorno, incluida
// la propia particula.
double Flock::vicsekAngle(int i) const {
    double sumSin = std::sin(angles_[i]);
    double sumCos = std::cos(angles_[i]);
    for (const int j : neighbors_[i]) {
        sumSin += std::sin(angles_[j]);
        sumCos += std::cos(angles_[j]);
    }
    return std::atan2(sumSin, sumCos);
}

// Modelo de votante: se copia la direccion de un unico vecino elegido al azar.
// Con voterIncludesSelf la propia particula entra en el sorteo, lo que ademas
// define el caso de una particula aislada (conserva su direccion).
double Flock::voterAngle(int i) {
    const std::size_t candidates = neighbors_[i].size() + (config_.voterIncludesSelf ? 1 : 0);
    if (candidates == 0) return angles_[i];

    std::uniform_int_distribution<std::size_t> pick(0, candidates - 1);
    const std::size_t k = pick(rng_);
    const int chosen = (k < neighbors_[i].size()) ? neighbors_[i][k] : i;
    return angles_[chosen];
}

void Flock::step() {
    const auto t0 = std::chrono::steady_clock::now();
    cim_.computeNeighbors(positions_, neighbors_);
    const auto t1 = std::chrono::steady_clock::now();
    neighborSeconds_ += std::chrono::duration<double>(t1 - t0).count();
    ++neighborCalls_;

    const int n = config_.N;
    for (int i = 0; i < n; ++i) {
        const double base = (config_.model == Model::Vicsek) ? vicsekAngle(i) : voterAngle(i);
        nextAngles_[i] = wrapAngle(base + noise_(rng_));
    }

    // Las posiciones avanzan con la velocidad en t, previa a la actualizacion.
    const double displacement = config_.speed * config_.dt;
    for (int i = 0; i < n; ++i) {
        positions_[i].x = box_.wrap(positions_[i].x + displacement * std::cos(angles_[i]));
        positions_[i].y = box_.wrap(positions_[i].y + displacement * std::sin(angles_[i]));
    }

    angles_.swap(nextAngles_);
    ++time_;
}

}  // namespace flock
