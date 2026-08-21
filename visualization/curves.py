"""Items (c), (d) y (e): observables escalares en el estacionario.

Lee todo el barrido, promedia primero en el tiempo dentro del estacionario de
cada corrida y despues entre realizaciones, y genera:

  va_vs_eta.png   (c) polarizacion contra ruido, una curva por densidad
  S_vs_eta.png    (d) fraccion de la componente gigante contra ruido
  va_vs_S.png     (e) polarizacion contra componente gigante
  resumen.csv     la tabla que respalda las tres figuras

Los dos modelos se superponen en cada figura, que es lo que pide el item (f).

    python3 visualization/curves.py
    python3 visualization/curves.py --error sem --models vicsek
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common


def summarise(arguments) -> list[dict]:
    """Un registro por (modelo, densidad, ruido) con los promedios y su error."""
    runs = common.read_index(arguments.sweep)
    models = arguments.models.split(",")
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for run in runs:
        if run["model"] in models:
            grouped[(run["model"], run["rho"], run["eta"])].append(run)

    records = []
    pending = []
    for (model, density, noise), group in sorted(grouped.items()):
        polarizations, fractions, starts = [], [], []
        converged = 0
        for run in group:
            table = common.read_observables(run["path"])
            # El estacionario se define con la polarizacion y la misma ventana
            # se usa para S, de modo que ambos escalares salen del mismo tramo.
            start = (arguments.teq if arguments.teq >= 0
                     else common.steady_state_start(table[:, 1]))
            start = min(start, len(table) - 2)
            starts.append(int(table[start, 0]))
            polarizations.append(table[start:, 1].mean())
            fractions.append(table[start:, 2].mean())
            converged += int(common.has_converged(table[:, 1]))
        if converged < len(group):
            pending.append((model, density, noise, len(group) - converged, len(group)))

        polarization, polarization_error = common.combine(polarizations, arguments.error)
        fraction, fraction_error = common.combine(fractions, arguments.error)
        records.append(
            {
                "model": model,
                "rho": density,
                "N": group[0]["N"],
                "eta": noise,
                "realizaciones": len(group),
                "teq_medio": float(np.mean(starts)),
                "va": polarization,
                "va_error": polarization_error,
                "S": fraction,
                "S_error": fraction_error,
            }
        )
    if not records:
        raise SystemExit("el barrido no tiene corridas de los modelos pedidos")
    if pending:
        print(f"aviso: {len(pending)} puntos con corridas que todavia derivan en el "
              "ultimo cuarto (hacen falta mas pasos):")
        for model, density, noise, bad, total in pending[:12]:
            print(f"  {model} rho={density:g} eta={noise:g}: {bad}/{total} realizaciones")
        if len(pending) > 12:
            print(f"  ... y {len(pending) - 12} puntos mas")
    return records


def group_by_series(records: list[dict]):
    series: dict[tuple, list[dict]] = defaultdict(list)
    for record in records:
        series[(record["model"], record["rho"])].append(record)
    for key in series:
        series[key].sort(key=lambda record: record["eta"])
    return series


def against_noise(records, observable: str, label: str, name: str, arguments) -> None:
    figure, axes = plt.subplots()
    for (model, density), points in sorted(group_by_series(records).items()):
        style = common.MODEL_STYLE[model]
        axes.errorbar(
            [point["eta"] for point in points],
            [point[observable] for point in points],
            yerr=[point[f"{observable}_error"] for point in points],
            color=common.density_color(density),
            linestyle=style["linestyle"], marker=style["marker"],
            markerfacecolor="none" if model == "voter" else None,
            label=f"$\\rho$ = {density:g} · {style['label']}",
        )
    axes.set_xlabel("$\\eta$ [rad]")
    axes.set_ylabel(label)
    axes.set_ylim(0.0, 1.05)
    axes.legend(ncol=2, fontsize=10)
    counts = {record["realizaciones"] for record in records}
    axes.set_title(
        f"{label} en el estacionario · $M$ = {min(counts)} realizaciones · "
        f"barra: {'desvio' if arguments.error == 'std' else 'error estandar'}",
        fontsize=11,
    )
    common.save(figure, name, arguments.out)


def polarization_against_fraction(records, arguments) -> None:
    figure, axes = plt.subplots()
    for (model, density), points in sorted(group_by_series(records).items()):
        style = common.MODEL_STYLE[model]
        axes.errorbar(
            [point["S"] for point in points],
            [point["va"] for point in points],
            xerr=[point["S_error"] for point in points],
            yerr=[point["va_error"] for point in points],
            color=common.density_color(density),
            linestyle=style["linestyle"], marker=style["marker"],
            markerfacecolor="none" if model == "voter" else None,
            alpha=0.9,
            label=f"$\\rho$ = {density:g} · {style['label']}",
        )
    axes.set_xlabel("$S$")
    axes.set_ylabel("$v_a$")
    axes.set_ylim(0.0, 1.05)
    axes.legend(ncol=2, fontsize=10)
    axes.set_title("Polarizacion contra fraccion en la componente gigante\n"
                   "cada punto es un valor de $\\eta$ en el estacionario", fontsize=11)
    common.save(figure, "va_vs_S.png", arguments.out)


def write_table(records: list[dict], arguments) -> None:
    arguments.out.mkdir(parents=True, exist_ok=True)
    path = arguments.out / "resumen.csv"
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    print(f"tabla: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sweep", type=Path, default=common.DATA / "sweep")
    parser.add_argument("--models", default="vicsek,voter")
    parser.add_argument("--error", choices=("std", "sem"), default="std",
                        help="desvio estandar entre realizaciones o error estandar")
    parser.add_argument("--teq", type=int, default=-1,
                        help="forzar el inicio del estacionario (-1 = criterio automatico)")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    common.use_report_style()
    records = summarise(arguments)
    against_noise(records, "va", "$v_a$", "va_vs_eta.png", arguments)
    against_noise(records, "S", "$S$", "S_vs_eta.png", arguments)
    polarization_against_fraction(records, arguments)
    write_table(records, arguments)
    if arguments.show:
        plt.show()


if __name__ == "__main__":
    main()
