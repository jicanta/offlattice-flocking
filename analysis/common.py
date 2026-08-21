"""Utilidades compartidas por las figuras del TP2.

El motor de C++ escribe archivos de texto en data/ y este modulo es el unico
lugar donde se los interpreta: el resto de los scripts solo grafica. Aca viven
tambien el criterio de estado estacionario y la convencion de barras de error,
que son decisiones del analisis y no de la simulacion.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIGURES = DATA / "figures"


# --------------------------------------------------------------------------
# Estilo
# --------------------------------------------------------------------------

def use_report_style() -> None:
    """Tipografia y tamanos legibles a tamano impreso, como pide la catedra."""
    matplotlib.rcParams.update(
        {
            "figure.figsize": (7.2, 4.8),
            "figure.dpi": 120,
            "savefig.dpi": 220,
            "savefig.bbox": "tight",
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman"],
            "font.size": 13,
            "axes.titlesize": 14,
            "axes.labelsize": 14,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "legend.fontsize": 11,
            "legend.frameon": True,
            "legend.framealpha": 0.9,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "lines.linewidth": 1.6,
            "lines.markersize": 5,
            "errorbar.capsize": 3,
        }
    )


DENSITY_COLOR = {2.0: "#1f77b4", 4.0: "#d62728", 8.0: "#2ca02c"}
MODEL_STYLE = {
    "vicsek": {"linestyle": "-", "marker": "o", "label": "Vicsek"},
    "voter": {"linestyle": "--", "marker": "s", "label": "votante"},
}


def density_color(density: float) -> str:
    if density in DENSITY_COLOR:
        return DENSITY_COLOR[density]
    palette = ["#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22"]
    return palette[int(density) % len(palette)]


def save(figure, name: str, directory: Path | None = None) -> Path:
    directory = directory or FIGURES
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    figure.savefig(path)
    print(f"figura: {path}")
    return path


# --------------------------------------------------------------------------
# Lectura de los archivos del motor
# --------------------------------------------------------------------------

def read_static(path: Path) -> dict:
    """static.txt: un `clave valor` por linea."""
    values: dict = {}
    for line in Path(path).read_text().splitlines():
        pieces = line.split()
        if len(pieces) != 2:
            continue
        key, value = pieces
        try:
            values[key] = float(value) if "." in value or "e" in value else int(value)
        except ValueError:
            values[key] = value
    return values


def read_observables(path: Path) -> np.ndarray:
    """observables.txt / archivos del sweep: columnas `t va S`."""
    table = np.loadtxt(path)
    if table.ndim == 1:
        table = table.reshape(1, -1)
    if table.shape[1] < 3:
        raise ValueError(
            f"{path} tiene {table.shape[1]} columnas; se esperaban 3 (t va S). "
            "Recompilar el motor y volver a simular."
        )
    return table


def read_index(directory: Path) -> list[dict]:
    """index.txt del sweep: una corrida por linea."""
    path = Path(directory) / "index.txt"
    if not path.exists():
        raise SystemExit(
            f"falta {path}. Correr primero:\n"
            "  cd engine && ./build/flock sweep --steps 20000"
        )
    runs = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        model, rho, count, eta, seed, steps, side, radius, speed, step, name = line.split()
        runs.append(
            {
                "model": model,
                "rho": float(rho),
                "N": int(count),
                "eta": float(eta),
                "seed": int(seed),
                "steps": int(steps),
                "L": float(side),
                "rc": float(radius),
                "v": float(speed),
                "dt": float(step),
                "path": Path(directory) / name,
            }
        )
    return runs


def frames(path: Path, count: int, stride: int = 1, limit: int | None = None):
    """Recorre dynamic.txt sin cargarlo entero: cede (t, x, y, theta)."""
    produced = 0
    with open(path) as handle:
        index = 0
        while True:
            header = handle.readline()
            if not header:
                return
            time = float(header.split()[0])
            if index % stride:
                for _ in range(count):
                    handle.readline()
            else:
                rows = [handle.readline().split() for _ in range(count)]
                if len(rows[-1]) != 3:
                    return
                table = np.array(rows, dtype=float)
                yield time, table[:, 0], table[:, 1], table[:, 2]
                produced += 1
                if limit is not None and produced >= limit:
                    return
            index += 1


# --------------------------------------------------------------------------
# Estado estacionario y promedios
# --------------------------------------------------------------------------

def block_means(values: np.ndarray, blocks: int) -> tuple[np.ndarray, int]:
    size = max(1, len(values) // blocks)
    count = len(values) // size
    means = np.array([values[k * size:(k + 1) * size].mean() for k in range(count)])
    return means, size


def steady_state_start(values: np.ndarray, blocks: int = 100) -> int:
    """Primer indice del estacionario: primer cruce con el valor de referencia.

    Se toma como referencia la media de la segunda mitad de la corrida, que es
    el valor del estacionario, y se recorre la serie suavizada por bloques hasta
    el primer bloque que cruza esa referencia. El transitorio es monotono (la
    polarizacion crece desde la condicion inicial desordenada, o el sistema se
    dispersa desde una condicion ordenada), asi que el cruce marca el final del
    transitorio sin depender de umbrales arbitrarios. Los promedios se toman de
    ahi en adelante.
    """
    values = np.asarray(values, dtype=float)
    if len(values) < 4:
        return 0
    reference = values[len(values) // 2:].mean()
    means, size = block_means(values, blocks)
    above = means[0] > reference
    for index, mean in enumerate(means):
        if (mean <= reference) if above else (mean >= reference):
            return index * size
    return len(values) // 2


def has_converged(values: np.ndarray, blocks: int = 100) -> bool:
    """Marca corridas donde la serie todavia deriva en el ultimo cuarto.

    Compara la media del tercer cuarto con la del cuarto cuarto: si difieren
    mas que la dispersion de las medias de bloque del ultimo cuarto, el
    estacionario no se alcanzo y la corrida necesita mas pasos.
    """
    values = np.asarray(values, dtype=float)
    if len(values) < 8:
        return False
    means, _ = block_means(values, blocks)
    third = means[len(means) // 2:3 * len(means) // 4]
    fourth = means[3 * len(means) // 4:]
    if len(third) < 2 or len(fourth) < 2:
        return True
    spread = fourth.std(ddof=1)
    return abs(third.mean() - fourth.mean()) <= max(2.0 * spread, 5e-3)


def steady_values(table: np.ndarray, column: int, start: int) -> np.ndarray:
    return table[start:, column]


def combine(per_run: list[float], error: str = "std") -> tuple[float, float]:
    """Promedio entre realizaciones y su barra de error.

    `std` es el desvio estandar entre realizaciones y `sem` el error estandar
    sigma/sqrt(M). Cual se usa hay que declararlo en el epigrafe de la figura.
    """
    sample = np.asarray(per_run, dtype=float)
    mean = float(sample.mean())
    if len(sample) < 2:
        return mean, 0.0
    deviation = float(sample.std(ddof=1))
    return mean, deviation if error == "std" else deviation / np.sqrt(len(sample))


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--out", type=Path, default=FIGURES,
                        help="directorio de salida de las figuras")
    parser.add_argument("--show", action="store_true",
                        help="abrir la figura en una ventana ademas de guardarla")
