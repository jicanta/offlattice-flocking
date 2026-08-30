"""Item (g): tiempo de la busqueda de vecinos del CIM contra N.

Lee la salida de `flock bench` y grafica el tiempo por busqueda promediado
sobre las repeticiones, con el desvio estandar entre repeticiones como barra
de error. Con --tp1 se superponen los tiempos del TP1 para la comparacion que
pide la consigna: el archivo tiene dos columnas, `N` y `ms_por_busqueda`.

    python3 visualization/bench.py
    python3 visualization/bench.py --bench data/bench/bench_l20.txt --tp1 reference/tp1_tiempos.txt --log
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common

STYLE = {
    "cim": {"color": "#1f77b4", "marker": "o", "label": "CIM (TP2)"},
    "brute": {"color": "#7f7f7f", "marker": "^", "label": "fuerza bruta (TP2)"},
}


def read_bench(path: Path) -> dict:
    rows = defaultdict(list)
    header = {}
    for line in Path(path).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        pieces = line.split()
        method, count, cells = pieces[0], int(pieces[1]), int(pieces[2])
        header.setdefault("L", pieces[3])
        if method == "cim":
            header.setdefault("M", cells)
        rows[(method, count)].append(float(pieces[8]))
    return rows, header


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bench", type=Path, default=common.BENCH / "bench_l20.txt")
    parser.add_argument("--tp1", type=Path, default=common.ROOT / "reference" / "tp1_tiempos.txt",
                        help="archivo con los tiempos del TP1: columnas N y ms")
    parser.add_argument("--log", action="store_true", help="ejes logaritmicos")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    if not arguments.bench.exists():
        raise SystemExit(f"falta {arguments.bench}. Correr primero:\n  make bench")

    common.use_report_style(arguments.estilo)
    rows, header = read_bench(arguments.bench)
    # El rotulo del eje vertical es largo y va rotado: con la tipografia de la
    # diapositiva no entra en el alto por defecto y savefig lo recorta, asi que
    # esta figura se pide mas alta que el resto.
    size = (6.8, 5.4) if common.STYLE == "diapositiva" else None
    figure, axes = plt.subplots(figsize=size)

    for method in ("cim", "brute"):
        counts = sorted({key[1] for key in rows if key[0] == method})
        if not counts:
            continue
        means, errors = [], []
        for count in counts:
            samples = np.array(rows[(method, count)])
            means.append(samples.mean())
            errors.append(samples.std(ddof=1) if len(samples) > 1 else 0.0)
        axes.errorbar(counts, means, yerr=errors, **STYLE[method])

    if arguments.tp1 and arguments.tp1.exists():
        reference = np.atleast_2d(np.loadtxt(arguments.tp1))
        axes.plot(reference[:, 0], reference[:, 1], color="#d62728", marker="s",
                  linestyle="--", label="CIM (TP1)")

    axes.set_xlabel("número de partículas $N$")
    # En estilo diapositiva la tipografia es casi el doble y el rotulo largo no
    # entra en el alto de la figura, asi que se abrevia sin perder la unidad.
    axes.set_ylabel("tiempo de búsqueda (ms)" if common.STYLE == "diapositiva"
                    else "tiempo por búsqueda de vecinos (ms)")
    if arguments.log:
        axes.set_xscale("log")
        axes.set_yscale("log")
    axes.legend()
    name = (f"tiempo_busqueda_vs_N_L{header.get('L', '?')}_M{header.get('M', '?')}"
            f"_cim_bruta_tp1{'_log' if arguments.log else ''}.png")
    common.save(figure, common.folder("g", arguments.figures), name)


if __name__ == "__main__":
    main()
