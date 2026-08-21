# TP2 — Autómata Off-Lattice: Bandadas de Agentes Autopropulsados

Simulación de Sistemas — ITBA. Motor en C++, modelo de Vicsek [1] y modelo de
votante [2] sobre una caja periódica, con búsqueda de vecinos por Cell Index
Method.

```
tp-2/
├── engine/           # C++: dinámica, CIM, fuerza bruta, timing
│   ├── include/      # flock, observables, neighbor_search, geometry, io…
│   └── src/          # main + un archivo por comando (simulate, sweep, bench)
├── visualization/    # Python: animaciones y figuras del informe
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

Barrer el espacio de parámetros que necesitan las curvas de los ítems (c), (d)
y (e). Cada corrida escribe solo su serie temporal de observables, no las
posiciones, y las corridas se reparten entre todos los núcleos:

```bash
./build/flock sweep --rhos 2,4,8 --etas 0:5:0.25 --seeds 5 --steps 20000
```

Medir el costo de la búsqueda de vecinos para el ítem (g):

```bash
./build/flock bench --ns 100,200,400,800,1600,3200 --steps 200 --repeats 3
```

## Salida

- `data/static.txt` — parámetros de la corrida, un `clave valor` por línea.
- `data/dynamic.txt` — por cuadro: una línea con `t` y luego `N` líneas `x y theta`.
- `data/observables.txt` — una línea `t va S` por paso.
- `data/sweep/` — una serie `t va S` por corrida del barrido, más `index.txt`
  con una línea por corrida (`model rho N eta seed steps L rc v dt archivo`).
- `data/bench.txt` — una línea por medición: `método N M L rc pasos repetición
  ms_totales ms_por_búsqueda`.

`--save-every k` ralea únicamente los cuadros de posiciones: los observables se
escriben en todos los pasos. Con `rho=8` y 20 000 pasos, guardar cada cuadro son
unos 530 MB, mientras que la serie de observables queda en 20 001 líneas. Por eso
`sweep` no guarda posiciones: las animaciones salen de corridas puntuales de
`simulate`.

## Análisis y figuras

`pip install -r requirements.txt` y después, desde la raíz del repositorio:

```bash
python3 visualization/animate.py --out-file data/figures/vicsek.mp4   # (a) animación
python3 visualization/animate.py --snapshots 0,100,2000               # (a) cuadros para el PDF
python3 visualization/temporal.py --mode eta --model vicsek --rho 4   # (b) va(t) y S(t)
python3 visualization/temporal.py --mode rho --model vicsek --eta 2   # (d) S(t) por densidad
python3 visualization/temporal.py --mode model --rho 4 --eta 2        # (f) Vicsek vs votante
python3 visualization/curves.py                                       # (c) (d) (e) + resumen.csv
python3 visualization/bench.py --tp1 data/tp1.txt                     # (g) tiempos contra el TP1
```

`dynamic.py` y `polarization.py` son entradas sueltas para mirar una corrida
puntual: la animación de un `dynamic.txt` y la evolución de `va` con un `t_eq`
elegido a mano. El resto trabaja sobre el barrido completo y comparte
`common.py`:

| Script | Qué hace |
|---|---|
| `dynamic.py` | animación de una corrida, `-N` y `L` salen de `static.txt` |
| `polarization.py` | `va(t)` de una corrida con `--teq` manual |
| `animate.py` | animación y tira de cuadros para el PDF |
| `temporal.py` | `va(t)` y `S(t)` con el `t_eq` automático |
| `curves.py` | curvas contra `eta`, `va` contra `S` y `resumen.csv` |
| `bench.py` | tiempos del CIM contra el TP1 |

Las flechas se dibujan con longitud fija (`--flecha`, `--arrow`): con `v = 0.03`
y `L = 10` el desplazamiento por paso es un 0.3 % de la caja, así que la flecha
indica dirección y no módulo. Como la rapidez es común a todas las partículas,
no se pierde información al hacerlo.

### Casos característicos para las animaciones

```bash
# transitorio: varios grupos, cada uno de un color, que se fusionan en uno solo
./build/flock simulate --model vicsek --rho 2 --eta 0.3 --steps 600 --seed 8
python3 visualization/animate.py --frames 300

# estacionario heterogéneo cerca de la transición: los grupos se arman y se deshacen
./build/flock simulate --model vicsek --rho 2 --eta 3 --steps 3000 --seed 5
python3 visualization/animate.py --desde 1000 --stride 3 --frames 500

# estacionario del votante: dominios de color que persisten indefinidamente
./build/flock simulate --model voter --rho 4 --eta 1 --steps 3000 --seed 5
python3 visualization/animate.py --desde 1000 --stride 3 --frames 500
```

`--desde` saltea el transitorio y anima solo el estacionario, que es lo que hay
que mostrar cuando la animación acompaña a un valor escalar del observable.

Las figuras van a `data/figures/`. El criterio de estado estacionario vive en
`visualization/common.py`: se toma como referencia la media de la segunda mitad de la
corrida y el estacionario arranca en el primer bloque que cruza esa referencia.
El mismo *t*eq se usa para `va` y para `S`. `curves.py` avisa qué puntos todavía
derivan en el último cuarto de la corrida, es decir cuáles necesitan más pasos;
`--teq` fuerza un valor único si se prefiere un criterio conservador y uniforme.

## Modelo

Actualización sincrónica. En cada paso los vecinos se calculan con las
posiciones en `t`, de ahí salen los ángulos en `t+1` y las posiciones avanzan
con la velocidad en `t`, como en la ecuación (1) de [1]:

```
x_i(t+1)     = x_i(t) + v_i(t) dt
theta_i(t+1) = base_i(t) + U[-eta/2, eta/2]
```

- **Vicsek**: `base_i` es el promedio vectorial de las direcciones dentro de
  `rc` **incluyendo a la propia partícula**, que es el criterio estándar fijado
  por la cátedra:

  ```
  base_i = atan2( sin(theta_i) + sum_j sin(theta_j),
                  cos(theta_i) + sum_j cos(theta_j) )
  ```

  La lista de vecinos nunca contiene a `i` (los pares se registran una sola vez,
  con `first < second`), así que la dirección propia entra exactamente una vez y
  no hay doble conteo. Una partícula sin vecinos conserva su dirección más el
  ruido.

- **Votante**: `base_i` es la dirección de un único vecino elegido al azar, que
  se copia tal cual —sin promediar— tomando su ángulo `theta_j(t)` del paso
  actual. Como las direcciones nuevas se escriben en un buffer aparte y recién
  se intercambian al final del paso, todas las copias de un mismo paso leen el
  estado en `t`.

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
