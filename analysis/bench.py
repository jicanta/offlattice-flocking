"""Item (g): tiempo de la busqueda de vecinos del CIM contra N.

Lee data/bench.txt (comando `flock bench`) y grafica el tiempo por busqueda
promediado sobre las repeticiones. Con --tp1 se superponen los tiempos del TP1
para la comparacion que pide la consigna: el archivo debe tener dos columnas,
`N` y `ms_por_busqueda`, una linea por medicion.

    python3 analysis/bench.py
    python3 analysis/bench.py --tp1 data/tp1.txt --log
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
    for line in Path(path).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        pieces = line.split()
        method, count, cells = pieces[0], int(pieces[1]), int(pieces[2])
        rows[(method, count, cells)].append(float(pieces[8]))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bench", type=Path, default=common.DATA / "bench.txt")
    parser.add_argument("--tp1", type=Path, default=None,
                        help="archivo con los tiempos del TP1: columnas N y ms")
    parser.add_argument("--log", action="store_true", help="ejes logaritmicos")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    if not arguments.bench.exists():
        raise SystemExit(
            f"falta {arguments.bench}. Correr primero:\n"
            "  cd engine && ./build/flock bench"
        )

    common.use_report_style()
    rows = read_bench(arguments.bench)
    figure, axes = plt.subplots()

    for method in ("cim", "brute"):
        counts = sorted({key[1] for key in rows if key[0] == method})
        if not counts:
            continue
        means, errors = [], []
        for count in counts:
            samples = np.concatenate([np.array(value) for key, value in rows.items()
                                      if key[0] == method and key[1] == count])
            means.append(samples.mean())
            errors.append(samples.std(ddof=1) if len(samples) > 1 else 0.0)
        axes.errorbar(counts, means, yerr=errors, **STYLE[method])

    if arguments.tp1:
        reference = np.loadtxt(arguments.tp1)
        reference = np.atleast_2d(reference)
        axes.plot(reference[:, 0], reference[:, 1], color="#d62728", marker="s",
                  linestyle="--", label="CIM (TP1)")

    axes.set_xlabel("$N$")
    axes.set_ylabel("tiempo por busqueda de vecinos [ms]")
    if arguments.log:
        axes.set_xscale("log")
        axes.set_yscale("log")
    axes.legend()
    axes.set_title("Costo de la busqueda de vecinos", fontsize=12)
    common.save(figure, "tiempos_cim.png", arguments.out)
    if arguments.show:
        plt.show()


if __name__ == "__main__":
    main()
