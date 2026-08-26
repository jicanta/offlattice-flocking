"""Items (c), (d), (e) y (f): observables escalares en el estacionario.

Lee data/sweep/resumen.csv (lo escribe summarise.py) y genera:

  c_va_vs_eta/   va contra eta, Vicsek, una curva por densidad
  d_clusters/    S contra eta, Vicsek, una curva por densidad
  e_va_vs_S/     va contra S, Vicsek, una curva por densidad
  f_votante/     lo mismo para el votante, mas las comparaciones:
                 va contra eta por densidad (Vicsek y votante en la misma
                 figura) y va contra S por densidad.

Todas las barras de error son el desvio estandar del observable sobre las
muestras estacionarias de las M realizaciones (common.steady_statistics).

    python3 visualization/curves.py
"""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

import common


def draw_against_noise(axes, points, observable, color, model, label):
    style = common.MODEL_STYLE[model]
    axes.errorbar(
        [point["eta"] for point in points],
        [point[observable] for point in points],
        yerr=[point[f"{observable}_std"] for point in points],
        color=color, linestyle=style["linestyle"], marker=style["marker"],
        markerfacecolor="none" if model == "voter" else None,
        label=label,
    )


def against_noise(records, models, rhos, observable, folder, name) -> None:
    """observable contra eta; una curva por (modelo, densidad)."""
    figure, axes = plt.subplots()
    for model in models:
        for rho in rhos:
            points = common.series_by(records, model, rho)
            if not points:
                continue
            label = (f"$\\rho$ = {rho:g}" if len(models) == 1
                     else f"{common.MODEL_LABEL[model]}" if len(rhos) == 1
                     else f"$\\rho$ = {rho:g} · {common.MODEL_LABEL[model]}")
            color = common.density_color(rho) if len(rhos) > 1 else common.MODEL_STYLE[model]["color"]
            draw_against_noise(axes, points, observable, color, model, label)
    axes.set_xlabel("$\\eta$ [rad]")
    axes.set_ylabel(common.LABEL[observable])
    if observable == "va":
        axes.set_ylim(0.0, 1.05)
    # Para S el rango util es angosto y se deja que matplotlib lo ajuste a los
    # datos, en vez de forzar [0, 1] y dejar la figura casi vacia.
    axes.legend(loc="best")
    common.save(figure, folder, name)


def against_fraction(records, models, rhos, folder, name) -> None:
    """va contra S; cada punto es un eta del barrido."""
    figure, axes = plt.subplots()
    for model in models:
        for rho in rhos:
            points = common.series_by(records, model, rho)
            if not points:
                continue
            style = common.MODEL_STYLE[model]
            label = (f"$\\rho$ = {rho:g}" if len(models) == 1
                     else f"{common.MODEL_LABEL[model]}" if len(rhos) == 1
                     else f"$\\rho$ = {rho:g} · {common.MODEL_LABEL[model]}")
            color = common.density_color(rho) if len(rhos) > 1 else style["color"]
            # Las barras (sobre todo sigma_S a rho = 2) son grandes frente al
            # rango de S: se dibujan tenues y sin remate para que los puntos
            # se lean primero; su tamano sigue siendo el de la Ec. del informe.
            axes.errorbar(
                [point["S"] for point in points],
                [point["va"] for point in points],
                xerr=[point["S_std"] for point in points],
                yerr=[point["va_std"] for point in points],
                color=color, linestyle=style["linestyle"], marker=style["marker"],
                markerfacecolor="none" if model == "voter" else None,
                elinewidth=0.7, capsize=0, ecolor=to_rgba(color, 0.35),
                label=label, zorder=3,
            )
    axes.set_xlabel("$S$")
    axes.set_ylabel("$v_a$")
    axes.set_ylim(0.0, 1.05)
    axes.set_xlim(right=1.005)
    axes.legend(loc="best")
    common.save(figure, folder, name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    common.use_report_style()
    records = common.read_summary(arguments.sweep / "resumen.csv")
    realizations = min(record["M"] for record in records)
    rhos = sorted({record["rho"] for record in records})
    tag = f"rho{common.joined(rhos)}_M{realizations}"

    for model in ("vicsek", "voter"):
        c = common.folder("c" if model == "vicsek" else "f", arguments.figures)
        d = common.folder("d" if model == "vicsek" else "f", arguments.figures)
        e = common.folder("e" if model == "vicsek" else "f", arguments.figures)
        against_noise(records, [model], rhos, "va", c, f"va_vs_eta_{model}_{tag}.png")
        if model == "voter":
            # La curva del votante va tambien en (c), junto a la de Vicsek.
            against_noise(records, [model], rhos, "va",
                          common.folder("c", arguments.figures), f"va_vs_eta_{model}_{tag}.png")
        against_noise(records, [model], rhos, "S", d, f"S_vs_eta_{model}_{tag}.png")
        against_fraction(records, [model], rhos, e, f"va_vs_S_{model}_{tag}.png")

    f = common.folder("f", arguments.figures)
    for rho in rhos:
        against_noise(records, ["vicsek", "voter"], [rho], "va", f,
                      f"va_vs_eta_vicsek_vs_voter_rho{common.number(rho)}_M{realizations}.png")
        against_fraction(records, ["vicsek", "voter"], [rho], f,
                         f"va_vs_S_vicsek_vs_voter_rho{common.number(rho)}_M{realizations}.png")


if __name__ == "__main__":
    main()
