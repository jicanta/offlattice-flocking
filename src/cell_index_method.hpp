#pragma once

#include <vector>

#include "vec2.hpp"

namespace flock {

// Lista de adyacencia: neighbors[i] contiene los indices j != i tales que
// d(i, j) <= rc bajo contorno periodico.
using NeighborLists = std::vector<std::vector<int>>;

// Cell Index Method off-lattice: divide la caja en M x M celdas de lado
// L/M >= rc y busca vecinos recorriendo solo las celdas adyacentes.
//
// Se usa el barrido "medio vecindario" (5 de las 9 celdas del entorno de Moore
// de rango 1): cada par se evalua una unica vez y se registra en ambos sentidos,
// lo que reduce a la mitad los calculos de distancia. Ese barrido solo es valido
// si M >= 3; por debajo de ese valor las celdas vecinas se solapan consigo mismas
// al envolver y la clase cae automaticamente a fuerza bruta O(N^2).
class CellIndexMethod {
public:
    // cellsPerSide <= 0 selecciona el maximo admisible, floor(L / rc).
    CellIndexMethod(const PeriodicBox& box, double rc, int cellsPerSide = 0);

    // Maximo M admisible para que el lado de celda no sea menor que rc.
    static int maxCellsPerSide(double side, double rc);

    int cellsPerSide() const { return m_; }
    double cellSide() const { return box_.side() / m_; }
    bool bruteForce() const { return bruteForce_; }

    // Llena out con los vecinos de cada particula. out se reutiliza entre pasos
    // (se limpia sin liberar la capacidad ya reservada).
    void computeNeighbors(const std::vector<Vec2>& positions, NeighborLists& out);

private:
    int cellIndex(const Vec2& p) const;
    void computeBruteForce(const std::vector<Vec2>& positions, NeighborLists& out) const;

    PeriodicBox box_;
    double rc_;
    double rcSquared_;
    int m_;
    bool bruteForce_;
    std::vector<std::vector<int>> cells_;
};

}  // namespace flock
