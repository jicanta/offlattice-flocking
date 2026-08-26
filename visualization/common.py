"""Utilidades compartidas por las figuras del TP2.

El motor de C++ escribe archivos de texto en data/ y este modulo es el unico
lugar donde se los interpreta: el resto de los scripts solo grafica. Aca viven
tambien el criterio de estado estacionario y la convencion de barras de error,
que son decisiones del analisis y no de la simulacion, y por eso estan en un
solo lugar: todas las figuras usan exactamente el mismo calculo.

Convenciones (las mismas en todas las figuras):

* Un "caso" es una terna (modelo, rho, eta). Cada caso tiene M realizaciones
  (semillas distintas) que solo difieren en la condicion inicial y en la
  secuencia de ruido.
* El inicio del estacionario t_eq se determina sobre la curva promedio de las
  M realizaciones de va(t), y es el mismo para todas ellas y para S. Asi el
  resultado no depende de la semilla.
* El valor escalar de un observable es el promedio de todas las muestras con
  t >= t_eq de las M realizaciones, y su barra de error es el desvio estandar
  de esas mismas muestras (ddof = 1). Esto es el "valor medio en el
  estacionario con su desvio" que pide la consigna.
* Las figuras no llevan titulo: los parametros van en el nombre del archivo y
  en el epigrafe del informe.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SWEEP = DATA / "sweep"
RUNS = DATA / "runs"
BENCH = DATA / "bench"
FIGURES = DATA / "figures"
SUMMARY = SWEEP / "resumen.csv"

# Carpetas de figuras, una por item del enunciado.
FOLDER_NAME = {
    "a": "a_animaciones",
    "b": "b_evolucion_temporal",
    "c": "c_va_vs_eta",
    "d": "d_clusters",
    "e": "e_va_vs_S",
    "f": "f_votante",
    "g": "g_tiempos_cim",
}


def folder(item: str, root: Path = FIGURES) -> Path:
    """Carpeta de figuras del item (a..g) del enunciado."""
    return Path(root) / FOLDER_NAME[item]

# Tamano de bloque (en pasos) con el que se suaviza la curva promedio para
# ubicar t_eq. Con 5000 pasos son 100 bloques.
BLOCK = 50

COLUMN = {"va": 1, "S": 2}
LABEL = {"va": "$v_a$", "S": "$S$"}


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
            "axes.labelsize": 15,
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
    "vicsek": {"linestyle": "-", "marker": "o", "label": "Vicsek", "color": "#1f77b4"},
    "voter": {"linestyle": "--", "marker": "s", "label": "votante", "color": "#d62728"},
}
MODEL_LABEL = {"vicsek": "Vicsek", "voter": "votante"}


def density_color(density: float) -> str:
    if density in DENSITY_COLOR:
        return DENSITY_COLOR[density]
    palette = ["#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22"]
    return palette[int(density) % len(palette)]


def number(value: float) -> str:
    """Numero corto para nombres de archivo: 0.5 -> '0.5', 2.0 -> '2'."""
    return f"{value:g}"


def joined(values) -> str:
    return "-".join(number(value) for value in values)


def save(figure, folder: Path, name: str) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    figure.savefig(path)
    matplotlib.pyplot.close(figure)
    print(f"figura: {shown(path)}")
    return path


def shown(path: Path) -> Path:
    """Ruta relativa al repositorio cuando se puede, para los mensajes."""
    return path.relative_to(ROOT) if path.is_relative_to(ROOT) else path


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


def read_index(directory: Path = SWEEP) -> list[dict]:
    """index.txt del sweep: una corrida por linea."""
    path = Path(directory) / "index.txt"
    if not path.exists():
        raise SystemExit(
            f"falta {path}. Correr primero:\n"
            "  make sweep"
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


def group_runs(runs: list[dict]) -> dict[tuple, list[dict]]:
    """Agrupa las corridas del sweep por caso (modelo, rho, eta)."""
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for run in runs:
        grouped[(run["model"], run["rho"], run["eta"])].append(run)
    for group in grouped.values():
        group.sort(key=lambda run: run["seed"])
    return dict(grouped)


def close(first: float, second: float) -> bool:
    return abs(first - second) < 1e-9


def find_case(grouped: dict, model: str, rho: float, eta: float) -> list[dict]:
    for (found_model, found_rho, found_eta), group in grouped.items():
        if found_model == model and close(found_rho, rho) and close(found_eta, eta):
            return group
    raise SystemExit(f"el barrido no tiene el caso {model}, rho={rho:g}, eta={eta:g}")


def load_case(group: list[dict]) -> np.ndarray:
    """Apila las M realizaciones de un caso: arreglo (M, pasos + 1, 3)."""
    tables = [read_observables(run["path"]) for run in group]
    length = min(len(table) for table in tables)
    return np.stack([table[:length] for table in tables])


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

def block_means(values: np.ndarray, block: int = BLOCK) -> np.ndarray:
    count = len(values) // block
    return values[: count * block].reshape(count, block).mean(axis=1)


def steady_state_start(mean_curve: np.ndarray, block: int = BLOCK) -> int:
    """Indice del inicio del estacionario sobre la curva promedio de va.

    Se toma como referencia la media de la segunda mitad de la curva promedio,
    que ya pertenece al estacionario, y se recorre la curva suavizada por
    bloques hasta el primer bloque que cruza esa referencia. El transitorio es
    monotono (la polarizacion crece desde la condicion inicial desordenada),
    asi que el cruce marca su final sin umbrales arbitrarios. Como se evalua
    sobre el promedio de las M realizaciones y no sobre cada una, t_eq es
    unico por caso y no depende de la semilla.
    """
    values = np.asarray(mean_curve, dtype=float)
    if len(values) < 2 * block:
        return 0
    reference = values[len(values) // 2:].mean()
    means = block_means(values, block)
    above = means[0] > reference
    for index, mean in enumerate(means):
        if (mean <= reference) if above else (mean >= reference):
            return index * block
    return len(values) // 2


def has_converged(mean_curve: np.ndarray, block: int = BLOCK) -> bool:
    """Falso si la curva promedio todavia deriva en el ultimo cuarto.

    Compara la media del tercer cuarto con la del cuarto cuarto: si difieren
    mas que la dispersion de las medias de bloque del ultimo cuarto, el
    estacionario no se alcanzo y el caso necesita mas pasos.
    """
    means = block_means(np.asarray(mean_curve, dtype=float), block)
    third = means[len(means) // 2: 3 * len(means) // 4]
    fourth = means[3 * len(means) // 4:]
    if len(third) < 2 or len(fourth) < 2:
        return True
    spread = fourth.std(ddof=1)
    return abs(third.mean() - fourth.mean()) <= max(2.0 * spread, 5e-3)


def steady_statistics(stack: np.ndarray, column: int, start: int) -> tuple[float, float]:
    """Promedio y desvio estandar de las muestras estacionarias de un caso.

    `stack` tiene forma (M, pasos, 3). Se agrupan todas las muestras con
    t >= t_eq de las M realizaciones en una sola poblacion, cuyo promedio es
    el valor escalar y cuyo desvio estandar (ddof = 1) es la barra de error.
    Esta es la unica definicion de barra de error usada en las figuras.
    """
    samples = stack[:, start:, column].ravel()
    if len(samples) < 2:
        return float(samples.mean()), 0.0
    return float(samples.mean()), float(samples.std(ddof=1))


def analyse_case(stack: np.ndarray) -> dict:
    """t_eq y escalares (con desvio) de un caso a partir de sus realizaciones."""
    mean_curve = stack[:, :, COLUMN["va"]].mean(axis=0)
    start = steady_state_start(mean_curve)
    start = min(start, stack.shape[1] - 2)
    polarization, polarization_std = steady_statistics(stack, COLUMN["va"], start)
    fraction, fraction_std = steady_statistics(stack, COLUMN["S"], start)
    return {
        "M": stack.shape[0],
        "teq": float(stack[0, start, 0]),
        "start": start,
        "converged": has_converged(mean_curve),
        "va": polarization,
        "va_std": polarization_std,
        "S": fraction,
        "S_std": fraction_std,
    }


# --------------------------------------------------------------------------
# Tabla resumen (la escriben summarise.py y la leen las curvas)
# --------------------------------------------------------------------------

SUMMARY_FIELDS = ["model", "rho", "N", "eta", "M", "steps", "teq",
                  "va", "va_std", "S", "S_std", "converged"]


def write_summary(records: list[dict], path: Path = SUMMARY) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    print(f"tabla: {shown(path)}")


def read_summary(path: Path = SUMMARY) -> list[dict]:
    if not path.exists():
        raise SystemExit(
            f"falta {path}. Correr primero:\n"
            "  python3 visualization/summarise.py   (o make summary)"
        )
    records = []
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            records.append(
                {
                    "model": row["model"],
                    "rho": float(row["rho"]),
                    "N": int(row["N"]),
                    "eta": float(row["eta"]),
                    "M": int(row["M"]),
                    "steps": int(row["steps"]),
                    "teq": float(row["teq"]),
                    "va": float(row["va"]),
                    "va_std": float(row["va_std"]),
                    "S": float(row["S"]),
                    "S_std": float(row["S_std"]),
                    "converged": row["converged"] == "True",
                }
            )
    return records


def series_by(records: list[dict], model: str, rho: float) -> list[dict]:
    points = [record for record in records
              if record["model"] == model and close(record["rho"], rho)]
    return sorted(points, key=lambda record: record["eta"])


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--sweep", type=Path, default=SWEEP,
                        help="directorio del barrido")
    parser.add_argument("--figures", type=Path, default=FIGURES,
                        help="raiz de las carpetas de figuras")
