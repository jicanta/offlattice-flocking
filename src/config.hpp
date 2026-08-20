#pragma once

#include <cstdint>
#include <string>

namespace flock {

// Regla de interaccion entre particulas.
//   Vicsek: promedia las direcciones de todos los vecinos.
//   Voter : copia la direccion de un unico vecino elegido al azar.
enum class Model { Vicsek, Voter };

std::string modelName(Model model);

struct Config {
    double L = 10.0;          // lado de la caja
    double rho = 4.0;         // densidad N / L^2
    int N = 0;                // 0 => se deriva de rho
    double rc = 1.0;          // radio de interaccion
    double speed = 0.03;      // modulo de la velocidad, |v|
    double dt = 1.0;          // paso temporal
    double eta = 0.0;         // amplitud del ruido, dtheta ~ U[-eta/2, eta/2]
    Model model = Model::Vicsek;
    bool voterIncludesSelf = true;  // la particula se cuenta como candidata a copiar
    long long steps = 1000;         // pasos de simulacion
    long long saveEvery = 1;        // se guarda un cuadro cada saveEvery pasos
    std::uint64_t seed = 1;
    int cellsPerSide = 0;           // M del CIM; 0 => maximo admisible
    std::string outDir = "output";

    // Completa N a partir de rho (o rho a partir de N) y valida los parametros.
    void resolve();
};

std::string usage(const char* program);

// Lanza std::runtime_error ante argumentos invalidos.
Config parseArgs(int argc, char** argv);

}  // namespace flock
