#include "cell_index_method.hpp"

#include <algorithm>
#include <stdexcept>

namespace flock {

namespace {

// Medio entorno de Moore de rango 1: la celda propia y cuatro adyacentes.
// Recorriendo solo estas, cada par de celdas vecinas se visita una sola vez.
constexpr int kHalfNeighborhood[5][2] = {{0, 0}, {1, 0}, {1, 1}, {0, 1}, {-1, 1}};

constexpr int kMinCellsForHalfScan = 3;

}  // namespace

int CellIndexMethod::maxCellsPerSide(double side, double rc) {
    if (rc <= 0.0) throw std::invalid_argument("rc debe ser positivo");
    const int m = static_cast<int>(side / rc);
    return std::max(m, 1);
}

CellIndexMethod::CellIndexMethod(const PeriodicBox& box, double rc, int cellsPerSide)
    : box_(box), rc_(rc), rcSquared_(rc * rc) {
    const int maxM = maxCellsPerSide(box.side(), rc);
    m_ = (cellsPerSide <= 0) ? maxM : cellsPerSide;
    if (m_ > maxM) {
        throw std::invalid_argument("M demasiado grande: el lado de celda L/M quedaria menor que rc");
    }
    bruteForce_ = (m_ < kMinCellsForHalfScan);
    cells_.resize(static_cast<std::size_t>(m_) * m_);
}

int CellIndexMethod::cellIndex(const Vec2& p) const {
    const double side = cellSide();
    int cx = static_cast<int>(p.x / side);
    int cy = static_cast<int>(p.y / side);
    // Blindaje contra redondeo en el borde superior de la caja.
    cx = std::min(std::max(cx, 0), m_ - 1);
    cy = std::min(std::max(cy, 0), m_ - 1);
    return cy * m_ + cx;
}

void CellIndexMethod::computeBruteForce(const std::vector<Vec2>& positions, NeighborLists& out) const {
    const int n = static_cast<int>(positions.size());
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            if (box_.distanceSquared(positions[i], positions[j]) <= rcSquared_) {
                out[i].push_back(j);
                out[j].push_back(i);
            }
        }
    }
}

void CellIndexMethod::computeNeighbors(const std::vector<Vec2>& positions, NeighborLists& out) {
    const int n = static_cast<int>(positions.size());
    if (static_cast<int>(out.size()) != n) out.resize(n);
    for (auto& list : out) list.clear();

    if (bruteForce_) {
        computeBruteForce(positions, out);
        return;
    }

    for (auto& cell : cells_) cell.clear();
    for (int i = 0; i < n; ++i) cells_[cellIndex(positions[i])].push_back(i);

    for (int cy = 0; cy < m_; ++cy) {
        for (int cx = 0; cx < m_; ++cx) {
            const std::vector<int>& self = cells_[cy * m_ + cx];
            if (self.empty()) continue;

            for (const auto& offset : kHalfNeighborhood) {
                // Las celdas vecinas envuelven junto con el contorno periodico.
                const int nx = (cx + offset[0] + m_) % m_;
                const int ny = (cy + offset[1] + m_) % m_;
                const std::vector<int>& other = cells_[ny * m_ + nx];
                const bool sameCell = (offset[0] == 0 && offset[1] == 0);

                for (std::size_t a = 0; a < self.size(); ++a) {
                    const int i = self[a];
                    // Dentro de la propia celda solo se evaluan los pares i < j.
                    for (std::size_t b = sameCell ? a + 1 : 0; b < other.size(); ++b) {
                        const int j = other[b];
                        if (box_.distanceSquared(positions[i], positions[j]) <= rcSquared_) {
                            out[i].push_back(j);
                            out[j].push_back(i);
                        }
                    }
                }
            }
        }
    }
}

}  // namespace flock
