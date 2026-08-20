#include <exception>
#include <iostream>

#include "config.hpp"
#include "flock.hpp"
#include "observables.hpp"
#include "output.hpp"

int main(int argc, char** argv) {
    using namespace flock;

    Config config;
    try {
        config = parseArgs(argc, argv);
    } catch (const std::exception& error) {
        if (std::string(error.what()) == "__help__") {
            std::cout << usage(argv[0]);
            return 0;
        }
        std::cerr << "error: " << error.what() << "\n\n" << usage(argv[0]);
        return 1;
    }

    try {
        Flock flock(config);
        TrajectoryWriter writer(config);

        std::cerr << "modelo " << modelName(config.model) << " | N " << config.N << " | L "
                  << config.L << " | rho " << config.rho << " | eta " << config.eta << " | M "
                  << flock.cim().cellsPerSide()
                  << (flock.cim().bruteForce() ? " (fuerza bruta)" : "") << '\n';

        writer.writeFrame(0, flock.positions(), flock.angles());
        writer.writeObservable(0, polarization(flock.angles()));

        for (long long t = 1; t <= config.steps; ++t) {
            flock.step();
            if (t % config.saveEvery == 0) {
                writer.writeFrame(t, flock.positions(), flock.angles());
                writer.writeObservable(t, polarization(flock.angles()));
            }
        }

        std::cerr << "va final " << polarization(flock.angles()) << '\n';
        if (flock.neighborCalls() > 0) {
            std::cerr << "CIM: " << flock.neighborSeconds() << " s en " << flock.neighborCalls()
                      << " pasos (" << flock.neighborSeconds() * 1e3 / flock.neighborCalls()
                      << " ms/paso)\n";
        }
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
