# offlattice-flocking

Motor de simulacion en C++ del ejercicio del TP2 de Simulacion de Sistemas:
**Automata Off-Lattice — bandadas de agentes autopropulsados**.

Implementa el modelo de Vicsek [1] y el modelo de votante [2] sobre una caja
cuadrada de lado *L* con condiciones periodicas de contorno, con busqueda de
vecinos por Cell Index Method (CIM) off-lattice.

Grupo 10 — Comision S2 — 2026 Q2.

## Compilacion

```bash
make          # binario ./sim, -O3
make debug    # -O0 -g con ASan/UBSan
make clean
```

Requiere g++ con C++17. No hay dependencias externas.

## Uso

```bash
./sim --model vicsek --rho 4 --eta 1.5 --steps 5000 --seed 1 --out output/run
./sim --help
```

| Opcion | Default | Descripcion |
|---|---|---|
| `--model <vicsek\|voter>` | `vicsek` | Regla de interaccion |
| `--L` | `10` | Lado de la caja |
| `--rho` | `4` | Densidad *N*/*L*²; *ρ* = 2, 4, 8 → *N* = 200, 400, 800 |
| `--N` | — | Numero de particulas; tiene prioridad sobre `--rho` |
| `--rc` | `1` | Radio de interaccion |
| `--v` | `0.03` | Modulo de la velocidad |
| `--dt` | `1` | Paso temporal |
| `--eta` | `0` | Amplitud del ruido, Δθ ~ U[−η/2, η/2] |
| `--steps` | `1000` | Pasos de simulacion |
| `--save-every` | `1` | Guardar un cuadro cada *k* pasos |
| `--seed` | `1` | Semilla del generador (una realizacion por semilla) |
| `--M` | `0` | Celdas por lado del CIM; 0 = maximo admisible, floor(*L*/*rc*) |
| `--voter-self` | `1` | El votante se incluye a si mismo entre los candidatos a copiar |
| `--out` | `output` | Directorio de salida |

## Salida

La simulacion solo escribe archivos de texto; la animacion y el analisis se
ejecutan despues, de forma independiente, tomando estos archivos como entrada.

- `static.txt` — parametros de la corrida, un `clave valor` por linea.
- `dynamic.txt` — por cuadro: una linea con *t* y luego *N* lineas `x y theta`.
- `polarization.txt` — una linea `t va` por cuadro.

## Modelo

Actualizacion sincronica. En cada paso se calculan los vecinos con las posiciones
en *t*; de ahi salen los angulos en *t*+1 y las posiciones avanzan con la
velocidad en *t*:

```
x_i(t+1) = x_i(t) + v_i(t) dt
theta_i(t+1) = base_i(t) + U[-eta/2, eta/2]
```

- **Vicsek**: `base_i` = `atan2(<sin theta>_r, <cos theta>_r)` sobre los vecinos
  dentro de *rc*, incluida la propia particula.
- **Votante**: `base_i` = direccion de un unico vecino elegido al azar. Por
  defecto la propia particula participa del sorteo (`--voter-self 1`), lo que
  ademas define el caso de una particula aislada: conserva su direccion.

## Cell Index Method

Grilla de *M* × *M* celdas de lado *L*/*M* ≥ *rc*, con barrido de medio vecindario
(5 de las 9 celdas del entorno de Moore de rango 1): cada par se evalua una sola
vez. El barrido requiere *M* ≥ 3; por debajo la clase cae automaticamente a
fuerza bruta *O*(*N*²). `--M 1` fuerza fuerza bruta y sirve como referencia.

El binario reporta por `stderr` el tiempo acumulado del CIM y el promedio por
paso, para el estudio de performance.

## Verificacion

- Con la misma semilla, `--M 10` (CIM) y `--M 1` (fuerza bruta) producen
  trayectorias identicas.
- *η* = 0 → *v*<sub>a</sub> → 1 en ambos modelos.
- *η* = 2π (ruido maximo) → *v*<sub>a</sub> ≈ 0.01–0.03, del orden de 1/√*N*
  con *N* = 400.

## Referencias

```
[1] T. Vicsek, A. Czirok, E. Ben-Jacob, I. Cohen y O. Shochet, "Novel type of phase
    transition in a system of self-driven particles", Physical Review Letters,
    vol. 75, nro. 6, p. 1226 (1995).
[2] E. S. Loscar, G. Baglietto y F. Vazquez, "Noisy multistate voter model for
    flocking in finite dimensions", Physical Review E, vol. 104, nro. 3,
    p. 034111 (2021).
```
