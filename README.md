# TP2 — Autómata Off-Lattice: Bandadas de Agentes Autopropulsados

Simulación de Sistemas — ITBA. Motor en C++, modelo de Vicsek [1] y modelo de
votante [2] sobre una caja periódica, con búsqueda de vecinos por Cell Index
Method.

```
tp-2/
├── engine/           # C++: dinámica, CIM, fuerza bruta, timing
│   ├── include/      # flock, observables, neighbor_search, geometry, io…
│   └── src/          # main + un archivo por comando (simulate)
├── data/             # salida generada (ignorado por git)
└── INFORME.md        # formato y estructura del informe
```

El CIM, la geometría periódica y el parseo de argumentos se reutilizan tal cual
del TP1, de modo que los tiempos de ambos trabajos son comparables.

El límite entre C++ y el análisis posterior son archivos de texto: el motor
escribe en `data/` y la animación y las figuras solo leen de ahí.

## Parámetros por defecto

`L=10`, `rc=1`, `v=0.03`, `dt=1`, contorno periódico, partículas puntuales.
Densidades del estudio: `rho=2, 4, 8`, es decir `N=200, 400, 800`.

## Compilación

```bash
cd engine
make
```

El binario queda en `engine/build/flock`. Los comandos de abajo se ejecutan
desde `engine/`, por eso las rutas por defecto apuntan a `../data/`.

## Uso

Correr el modelo estándar y guardar la trayectoria:

```bash
./build/flock simulate --model vicsek --rho 4 --eta 1.5 --steps 5000 --seed 1
```

Correr el modelo de votante desde la misma condición inicial:

```bash
./build/flock simulate --model voter --rho 4 --eta 1.5 --steps 5000 --seed 1
```

`--n` tiene prioridad sobre `--rho`. `--m` por defecto usa el máximo admitido,
`M = 9` para `L=10` y `rc=1`. `--method brute` corre fuerza bruta y sirve como
referencia de tiempos y de correctitud: con la misma semilla ambos métodos
producen trayectorias idénticas.

`--voter-strict` excluye a la partícula del sorteo del modelo de votante. Por
defecto participa, lo que además define el caso de una partícula aislada:
conserva su dirección.

## Salida

- `data/static.txt` — parámetros de la corrida, un `clave valor` por línea.
- `data/dynamic.txt` — por cuadro: una línea con `t` y luego `N` líneas `x y theta`.
- `data/polarization.txt` — una línea `t va` por cuadro.

`--save-every k` ralea únicamente los cuadros de posiciones: `polarization.txt`
se escribe en todos los pasos. Con `rho=8` y 20 000 pasos, guardar cada cuadro
son unos 530 MB, mientras que la serie del observable queda en 20 001 líneas.

## Modelo

Actualización sincrónica. En cada paso los vecinos se calculan con las
posiciones en `t`, de ahí salen los ángulos en `t+1` y las posiciones avanzan
con la velocidad en `t`, como en la ecuación (1) de [1]:

```
x_i(t+1)     = x_i(t) + v_i(t) dt
theta_i(t+1) = base_i(t) + U[-eta/2, eta/2]
```

- **Vicsek**: `base_i` es el promedio vectorial de las direcciones dentro de
  `rc`, incluida la propia partícula.
- **Votante**: `base_i` es la dirección de un único vecino elegido al azar.

## Verificación

- `--method cim` y `--method brute` con la misma semilla producen la misma
  trayectoria.
- `eta = 0` lleva `va` a 1 en ambos modelos.
- `eta = 2*pi` deja `va` en el orden de `1/sqrt(N)`.
- Con `N = 800` y 2000 pasos: CIM 1.36 ms por búsqueda contra 3.72 ms de fuerza
  bruta.

## Referencias

```
[1] T. Vicsek, A. Czirok, E. Ben-Jacob, I. Cohen y O. Shochet, "Novel type of phase
    transition in a system of self-driven particles", Physical Review Letters,
    vol. 75, nro. 6, p. 1226 (1995).
[2] E. S. Loscar, G. Baglietto y F. Vazquez, "Noisy multistate voter model for
    flocking in finite dimensions", Physical Review E, vol. 104, nro. 3,
    p. 034111 (2021).
```
