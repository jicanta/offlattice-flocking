#include "output.hpp"

#include <filesystem>
#include <iomanip>
#include <stdexcept>

namespace flock {

namespace {

std::ofstream openOrThrow(const std::filesystem::path& path) {
    std::ofstream file(path);
    if (!file) throw std::runtime_error("no se pudo escribir " + path.string());
    return file;
}

}  // namespace

TrajectoryWriter::TrajectoryWriter(const Config& config) {
    const std::filesystem::path dir(config.outDir);
    std::filesystem::create_directories(dir);

    std::ofstream staticFile = openOrThrow(dir / "static.txt");
    staticFile << std::setprecision(10);
    staticFile << "model " << modelName(config.model) << "\n"
               << "N " << config.N << "\n"
               << "L " << config.L << "\n"
               << "rho " << config.rho << "\n"
               << "rc " << config.rc << "\n"
               << "v " << config.speed << "\n"
               << "dt " << config.dt << "\n"
               << "eta " << config.eta << "\n"
               << "steps " << config.steps << "\n"
               << "save_every " << config.saveEvery << "\n"
               << "seed " << config.seed << "\n";

    dynamic_ = openOrThrow(dir / "dynamic.txt");
    observable_ = openOrThrow(dir / "polarization.txt");
    dynamic_ << std::fixed << std::setprecision(6);
    observable_ << std::fixed << std::setprecision(6);
}

void TrajectoryWriter::writeFrame(long long t, const std::vector<Vec2>& positions,
                                  const std::vector<double>& angles) {
    dynamic_ << t << '\n';
    for (std::size_t i = 0; i < positions.size(); ++i) {
        dynamic_ << positions[i].x << ' ' << positions[i].y << ' ' << angles[i] << '\n';
    }
}

void TrajectoryWriter::writeObservable(long long t, double polarization) {
    observable_ << t << ' ' << polarization << '\n';
}

}  // namespace flock
