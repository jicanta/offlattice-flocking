#include "config.hpp"

#include <cmath>
#include <sstream>
#include <stdexcept>
#include <string>

namespace flock {

std::string modelName(Model model) {
    return model == Model::Vicsek ? "vicsek" : "voter";
}

void Config::resolve() {
    if (L <= 0.0) throw std::runtime_error("L debe ser positivo");
    if (rc <= 0.0) throw std::runtime_error("rc debe ser positivo");
    if (speed < 0.0) throw std::runtime_error("v no puede ser negativo");
    if (dt <= 0.0) throw std::runtime_error("dt debe ser positivo");
    if (eta < 0.0) throw std::runtime_error("eta no puede ser negativo");
    if (steps < 0) throw std::runtime_error("steps no puede ser negativo");
    if (saveEvery <= 0) throw std::runtime_error("save-every debe ser positivo");

    if (N > 0) {
        rho = static_cast<double>(N) / (L * L);
    } else {
        if (rho <= 0.0) throw std::runtime_error("se requiere N > 0 o rho > 0");
        N = static_cast<int>(std::llround(rho * L * L));
        if (N <= 0) throw std::runtime_error("rho * L^2 arroja N = 0");
        // rho efectiva tras redondear N a entero.
        rho = static_cast<double>(N) / (L * L);
    }
}

std::string usage(const char* program) {
    std::ostringstream os;
    os << "Uso: " << program << " [opciones]\n"
       << "\n"
       << "  --model <vicsek|voter>  regla de interaccion (default: vicsek)\n"
       << "  --L <double>            lado de la caja (default: 10)\n"
       << "  --rho <double>          densidad N/L^2 (default: 4)\n"
       << "  --N <int>               numero de particulas; tiene prioridad sobre --rho\n"
       << "  --rc <double>           radio de interaccion (default: 1)\n"
       << "  --v <double>            modulo de la velocidad (default: 0.03)\n"
       << "  --dt <double>           paso temporal (default: 1)\n"
       << "  --eta <double>          amplitud del ruido (default: 0)\n"
       << "  --steps <int>           pasos de simulacion (default: 1000)\n"
       << "  --save-every <int>      guardar un cuadro cada k pasos (default: 1)\n"
       << "  --seed <int>            semilla del generador (default: 1)\n"
       << "  --M <int>               celdas por lado del CIM; 0 = maximo (default: 0)\n"
       << "  --voter-self <0|1>      el votante puede copiarse a si mismo (default: 1)\n"
       << "  --out <dir>             directorio de salida (default: output)\n"
       << "  --help                  esta ayuda\n";
    return os.str();
}

namespace {

double toDouble(const std::string& flag, const std::string& value) {
    try {
        return std::stod(value);
    } catch (const std::exception&) {
        throw std::runtime_error("valor no numerico para " + flag + ": " + value);
    }
}

long long toLongLong(const std::string& flag, const std::string& value) {
    try {
        return std::stoll(value);
    } catch (const std::exception&) {
        throw std::runtime_error("valor no entero para " + flag + ": " + value);
    }
}

}  // namespace

Config parseArgs(int argc, char** argv) {
    Config cfg;
    bool explicitN = false;

    for (int i = 1; i < argc; ++i) {
        const std::string flag = argv[i];
        if (flag == "--help" || flag == "-h") {
            throw std::runtime_error("__help__");
        }
        if (i + 1 >= argc) throw std::runtime_error("falta el valor de " + flag);
        const std::string value = argv[++i];

        if (flag == "--model") {
            if (value == "vicsek") {
                cfg.model = Model::Vicsek;
            } else if (value == "voter") {
                cfg.model = Model::Voter;
            } else {
                throw std::runtime_error("modelo desconocido: " + value);
            }
        } else if (flag == "--L") {
            cfg.L = toDouble(flag, value);
        } else if (flag == "--rho") {
            cfg.rho = toDouble(flag, value);
        } else if (flag == "--N") {
            cfg.N = static_cast<int>(toLongLong(flag, value));
            explicitN = true;
        } else if (flag == "--rc") {
            cfg.rc = toDouble(flag, value);
        } else if (flag == "--v") {
            cfg.speed = toDouble(flag, value);
        } else if (flag == "--dt") {
            cfg.dt = toDouble(flag, value);
        } else if (flag == "--eta") {
            cfg.eta = toDouble(flag, value);
        } else if (flag == "--steps") {
            cfg.steps = toLongLong(flag, value);
        } else if (flag == "--save-every") {
            cfg.saveEvery = toLongLong(flag, value);
        } else if (flag == "--seed") {
            cfg.seed = static_cast<std::uint64_t>(toLongLong(flag, value));
        } else if (flag == "--M") {
            cfg.cellsPerSide = static_cast<int>(toLongLong(flag, value));
        } else if (flag == "--voter-self") {
            cfg.voterIncludesSelf = (toLongLong(flag, value) != 0);
        } else if (flag == "--out") {
            cfg.outDir = value;
        } else {
            throw std::runtime_error("opcion desconocida: " + flag);
        }
    }

    if (!explicitN) cfg.N = 0;
    cfg.resolve();
    return cfg;
}

}  // namespace flock
