#pragma once

#include <cmath>

namespace flock {

// Punto/vector en el plano. La simulacion es off-lattice: las posiciones son
// continuas dentro de la caja de lado L.
struct Vec2 {
    double x = 0.0;
    double y = 0.0;
};

inline Vec2 operator+(const Vec2& a, const Vec2& b) { return {a.x + b.x, a.y + b.y}; }
inline Vec2 operator-(const Vec2& a, const Vec2& b) { return {a.x - b.x, a.y - b.y}; }
inline Vec2 operator*(const Vec2& a, double s) { return {a.x * s, a.y * s}; }

// Caja cuadrada de lado L con condiciones periodicas de contorno.
class PeriodicBox {
public:
    explicit PeriodicBox(double side) : side_(side) {}

    double side() const { return side_; }

    // Reingresa una coordenada al intervalo [0, L).
    double wrap(double c) const {
        c = std::fmod(c, side_);
        if (c < 0.0) c += side_;
        // fmod puede devolver exactamente L por redondeo al sumar side_.
        if (c >= side_) c = 0.0;
        return c;
    }

    Vec2 wrap(const Vec2& p) const { return {wrap(p.x), wrap(p.y)}; }

    // Componente de la separacion minima segun convencion de imagen minima.
    double minimumImage(double d) const { return d - side_ * std::round(d / side_); }

    // Distancia al cuadrado entre dos puntos bajo contorno periodico.
    double distanceSquared(const Vec2& a, const Vec2& b) const {
        const double dx = minimumImage(a.x - b.x);
        const double dy = minimumImage(a.y - b.y);
        return dx * dx + dy * dy;
    }

private:
    double side_;
};

}  // namespace flock
