"""Items (c), (d), (e) y (f): observables escalares en el estacionario.

Lee data/sweep/resumen.csv (lo escribe summarise.py) y genera:

  c_va_vs_eta/   va contra eta, una curva por densidad (Vicsek y votante)
  d_clusters/    S contra eta, una curva por densidad (Vicsek y votante)
  e_va_vs_S/     va contra S, una curva por densidad (Vicsek y votante)
  f_votante/     las mismas figuras del votante, mas las comparaciones de
                 (c), (d) y (e) con los dos modelos superpuestos, una figura
                 por densidad.

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
            label = (f"$\\rho$ = {common.density_label(rho)}" if len(models) == 1
                     else f"{common.MODEL_LABEL[model]}" if len(rhos) == 1
                     else f"$\\rho$ = {common.density_label(rho)} · {common.MODEL_LABEL[model]}")
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
            label = (f"$\\rho$ = {common.density_label(rho)}" if len(models) == 1
                     else f"{common.MODEL_LABEL[model]}" if len(rhos) == 1
                     else f"$\\rho$ = {common.density_label(rho)} · {common.MODEL_LABEL[model]}")
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
    parser.add_argument("--items", default="c,d,e,f",
                        help="items del enunciado a generar, separados por coma. "
                             "El estudio extendido de clusters usa --items d,e,f, "
                             "porque las densidades 1/(k*pi) solo entran ahi.")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    items = {piece.strip() for piece in arguments.items.split(",") if piece.strip()}
    unknown = items - set(common.FOLDER_NAME)
    if unknown:
        raise SystemExit(f"item desconocido: {', '.join(sorted(unknown))}")

    common.use_report_style()
    records = common.read_summary(arguments.sweep / "resumen.csv")
    realizations = min(record["M"] for record in records)
    rhos = sorted({record["rho"] for record in records})
    tag = f"rho{common.joined_densities(rhos)}_M{realizations}"
    figures = arguments.figures

    # Cada figura se dibuja en la carpeta de su item; ademas, las del votante se
    # duplican en la del item (f), que es donde el enunciado pide repetir (c),
    # (d) y (e) para la segunda regla de interaccion. Un item que no se pidio no
    # se dibuja en ninguna de las dos carpetas.
    def destinations(item: str, model: str) -> list:
        if item not in items:
            return []
        wanted = [item] + (["f"] if model == "voter" and "f" in items else [])
        return [common.folder(name, figures) for name in dict.fromkeys(wanted)]

    for model in ("vicsek", "voter"):
        for item, observable in (("c", "va"), ("d", "S")):
            for destination in destinations(item, model):
                against_noise(records, [model], rhos, observable, destination,
                              f"{observable}_vs_eta_{model}_{tag}.png")
        for destination in destinations("e", model):
            against_fraction(records, [model], rhos, destination,
                             f"va_vs_S_{model}_{tag}.png")

    if "f" not in items:
        return
    f = common.folder("f", figures)
    for rho in rhos:
        token = common.density_number(rho)
        if "c" in items:
            against_noise(records, ["vicsek", "voter"], [rho], "va", f,
                          f"va_vs_eta_vicsek_vs_voter_rho{token}_M{realizations}.png")
        if "d" in items:
            against_noise(records, ["vicsek", "voter"], [rho], "S", f,
                          f"S_vs_eta_vicsek_vs_voter_rho{token}_M{realizations}.png")
        if "e" in items:
            against_fraction(records, ["vicsek", "voter"], [rho], f,
                             f"va_vs_S_vicsek_vs_voter_rho{token}_M{realizations}.png")


if __name__ == "__main__":
    main()
