# TP2 — Autómata Off-Lattice: Bandadas de Agentes Autopropulsados

Simulación de Sistemas — ITBA. Motor en C++, modelo de Vicsek [1] y modelo de
votante [2] sobre una caja periódica, con búsqueda de vecinos por Cell Index
Method.

```
tp-2/
├── Makefile          # todo el flujo: build, sweep, animations, bench, figures
├── engine/           # C++: dinámica, CIM, fuerza bruta, timing
│   ├── include/      # flock, observables, neighbor_search, geometry, io…
│   └── src/          # main + un archivo por comando (simulate, sweep, bench)
├── visualization/    # Python: resumen del barrido, animaciones y figuras
├── reference/        # tiempos del TP1 para el ítem (g)
├── report/           # informe y presentación en LaTeX
├── data/             # salida generada (ignorada por git)
│   ├── sweep/        #   series t va S de cada corrida del barrido + resumen.csv
│   ├── runs/<caso>/  #   corridas con posiciones para las animaciones
│   ├── bench/        #   tiempos del CIM
│   └── figures/      #   una carpeta por ítem del enunciado (a … g)
└── INFORME.md        # formato del informe y notas de la cátedra
```

El CIM, la geometría periódica y el parseo de argumentos se reutilizan tal cual
del TP1, de modo que los tiempos de ambos trabajos son comparables.

El límite entre C++ y el análisis posterior son archivos de texto: el motor
escribe en `data/` y la animación y las figuras solo leen de ahí.

## Parámetros por defecto

`L=10`, `rc=1`, `v=0.03`, `dt=1`, contorno periódico, partículas puntuales.
Densidades del estudio: `rho=2, 4, 8`, es decir `N=200, 400, 800`.

## Flujo completo

```bash
pip install -r requirements.txt
make sweep        # barrido: 2 modelos x 3 densidades x 21 ruidos x 20 semillas
make animations   # corridas características + mp4 + tiras de cuadros
make bench        # tiempos del CIM con la caja del TP1 (máquina descargada)
make figures      # resumen.csv + todas las figuras en data/figures/<item>/
```

`make all` encadena los cuatro. Las variables del barrido se pueden pisar:
`make sweep SEEDS=30 ETAS=0:5:0.5 STEPS=8000`. El barrido reparte las corridas
entre todos los núcleos y tarda del orden de una hora con los valores por
defecto.

## Convenciones del análisis

Están implementadas una sola vez en `visualization/common.py` y las usan todas
las figuras:

- **Caso** = (modelo, ρ, η). Cada caso tiene `M` realizaciones con semillas
  distintas (`M = 20` por defecto), que sólo difieren en la condición inicial y
  en la secuencia de ruido.
- **Inicio del estacionario `t_eq`**: se determina sobre la curva *promedio* de
  las `M` realizaciones de `va(t)` (primer bloque de 50 pasos que cruza la media
  de la segunda mitad). Es único por caso, el mismo para `va` y para `S`, y no
  depende de la semilla.
- **Valor escalar y barra de error**: promedio y desvío estándar (`ddof=1`) de
  *todas* las muestras con `t ≥ t_eq` de las `M` realizaciones. Es la misma
  definición en `va` vs `η`, `S` vs `η`, `va` vs `S` y en las bandas de las
  evoluciones temporales. Para los tiempos del CIM, la barra es el desvío
  estándar entre repeticiones.
- **Sin títulos en las figuras**: los parámetros van en el nombre del archivo
  (`va_vs_eta_vicsek_rho2-4-8_M20.png`) y en el epígrafe del informe.

## Motor

```bash
cd engine && make            # binario en engine/build/flock
./build/flock simulate --model vicsek --rho 4 --eta 1.5 --steps 5000 --seed 1 --dir ../data/runs/prueba
./build/flock sweep --rhos 2,4,8 --etas 0:5:0.25 --seeds 20 --steps 5000
./build/flock bench --l 20 --ms 13 --ns 100,200,400,800 --steps 200 --repeats 5
```

`--n` tiene prioridad sobre `--rho`. `--m` por defecto usa el máximo admitido,
`M = 9` para `L=10` y `rc=1`. `--method brute` corre fuerza bruta y sirve como
referencia de tiempos y de correctitud: con la misma semilla ambos métodos
producen trayectorias idénticas. `--voter-strict` excluye a la partícula del
sorteo del modelo de votante; por defecto participa, lo que además define el
caso de una partícula aislada: conserva su dirección.

Salida:

- `static.txt` — parámetros de la corrida, un `clave valor` por línea.
- `dynamic.txt` — por cuadro: una línea con `t` y luego `N` líneas `x y theta`.
- `observables.txt` — una línea `t va S` por paso.
- `data/sweep/` — una serie `t va S` por corrida, más `index.txt` con una línea
  por corrida (`model rho N eta seed steps L rc v dt archivo`).
- `data/bench/bench_l20.txt` — una línea por medición: `método N M L rc pasos
  repetición ms_totales ms_por_búsqueda`.

`--save-every k` ralea únicamente los cuadros de posiciones: los observables se
escriben en todos los pasos. `sweep` no guarda posiciones: las animaciones
salen de corridas puntuales de `simulate --dir`.

## Figuras

| Script | Ítem | Qué hace |
|---|---|---|
| `summarise.py` | — | barrido → `data/sweep/resumen.csv` (t_eq, ⟨va⟩ ± σ, ⟨S⟩ ± σ por caso) |
| `animate.py` | (a) | animación y tira de cuadros de una corrida de `data/runs/` |
| `temporal.py` | (b) (d) (f) | `va(t)` y `S(t)`: un caso con sus `M` realizaciones, o promedios superpuestos |
| `curves.py` | (c) (d) (e) (f) | `va` vs `η`, `S` vs `η`, `va` vs `S`, y las comparaciones Vicsek–votante |
| `bench.py` | (g) | tiempos del CIM contra `N`, con los del TP1 superpuestos |

Sin argumentos, `temporal.py` y `curves.py` generan el juego completo de figuras
del informe. Para una figura puntual:

```bash
python3 visualization/temporal.py --model voter --rho 4 --eta 0.5 --item f
python3 visualization/temporal.py --model vicsek --rho 2 --etas 0.5,1,2,3,4
python3 visualization/animate.py --run data/runs/vicsek_rho4_eta0.5 --desde 1000
python3 visualization/animate.py --run data/runs/vicsek_rho4_eta0.5 --snapshots 0,250,1000,3000
```

Las flechas se dibujan con longitud fija (`--arrow`): con `v = 0.03` y `L = 10`
el desplazamiento por paso es un 0.3 % de la caja, así que la flecha indica
dirección y no módulo. Como la rapidez es común a todas las partículas, no se
pierde información al hacerlo. `--desde` saltea el transitorio y anima solo el
estacionario.

Caso complementario, **fuera de los parámetros del enunciado** (que fija
`L = 10` y `rho = 2, 4, 8`), útil para discutir el ítem (e) porque es el único
régimen que da `S < 1` con `va` alto:

```bash
cd engine && ./build/flock simulate --l 40 --rho 0.6 --eta 0.2 --steps 8000 --seed 5 --save-every 25 --dir ../data/runs/vicsek_L40_rho0.6_eta0.2
python3 visualization/animate.py --run data/runs/vicsek_L40_rho0.6_eta0.2 --desde 2000 --frames 250 --arrow 1.2
```

## Referencias

[1] T. Vicsek, A. Czirók, E. Ben-Jacob, I. Cohen y O. Shochet, Phys. Rev. Lett. 75, 1226 (1995).
[2] E. S. Loscar, G. Baglietto y F. Vazquez, Phys. Rev. E 104, 034111 (2021).
