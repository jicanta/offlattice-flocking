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

Con --sweeps se unen los resumenes de varios barridos, de modo que las
densidades del enunciado y las de 1/(k*pi) entren en la misma figura. Es lo
que piden los items (d) y (e): S solo recorre todo [0, 1] si se ven juntas una
densidad muy por encima del umbral de percolacion y otra por debajo.

    python3 visualization/curves.py --pares
    python3 visualization/curves.py --sweeps data/sweep,data/sweep_clusters \
        --rhos 8,2,0.31831,0.106103 --items d,e,f
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


# Aro alrededor de los puntos cuya corrida se muestra como animacion en la
# presentacion: asi la diapositiva une "la data" (el cuadro animado) con el
# punto del barrido que le corresponde. El color es el acento de los slides.
HIGHLIGHT_COLOR = "#c55a11"


def draw_highlights(axes, points, observable, model, rho, highlights) -> None:
    for spec_model, spec_rho, spec_eta in highlights:
        if spec_model != model or not common.close(spec_rho, rho):
            continue
        for point in points:
            if common.close(point["eta"], spec_eta):
                axes.scatter([point["eta"]], [point[observable]],
                             s=240, facecolors="none",
                             edgecolors=HIGHLIGHT_COLOR, linewidths=2.4,
                             zorder=6)


def against_noise(records, models, rhos, observable, folder, name, full=False,
                  highlights=()) -> None:
    """observable contra eta; una curva por (modelo, densidad)."""
    figure, axes = plt.subplots()
    for model in models:
        for rho in rhos:
            points = common.series_by(records, model, rho)
            if not points:
                continue
            label = (common.density_legend(rho) if len(models) == 1
                     else f"{common.MODEL_LABEL[model]}" if len(rhos) == 1
                     else f"{common.density_legend(rho)} · {common.MODEL_LABEL[model]}")
            color = common.density_color(rho) if len(rhos) > 1 else common.MODEL_STYLE[model]["color"]
            draw_against_noise(axes, points, observable, color, model, label)
            draw_highlights(axes, points, observable, model, rho, highlights)
    axes.set_xlabel(common.AXIS_NOISE)
    axes.set_ylabel(common.AXIS[observable])
    # va siempre va en [0, 1]. Para S el rango util es angosto cuando todas las
    # densidades estan por encima del umbral de percolacion, y ahi se deja que
    # matplotlib lo ajuste a los datos en vez de dejar la figura casi vacia;
    # cuando la figura mezcla densidades altas y bajas (full), S recorre todo
    # el intervalo y el eje se fija en [0, 1] para que las curvas sean
    # comparables entre si de un vistazo.
    if observable == "va" or full:
        axes.set_ylim(0.0, 1.05)
    axes.legend(loc="best")
    common.save(figure, folder, name)


def against_fraction(records, models, rhos, folder, name, full=False) -> None:
    """va contra S; cada punto es un eta del barrido."""
    figure, axes = plt.subplots()
    for model in models:
        for rho in rhos:
            points = common.series_by(records, model, rho)
            if not points:
                continue
            style = common.MODEL_STYLE[model]
            label = (common.density_legend(rho) if len(models) == 1
                     else f"{common.MODEL_LABEL[model]}" if len(rhos) == 1
                     else f"{common.density_legend(rho)} · {common.MODEL_LABEL[model]}")
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
    axes.set_xlabel(common.AXIS["S"])
    axes.set_ylabel(common.AXIS["va"])
    axes.set_ylim(0.0, 1.05)
    # Ambos observables son fracciones: cuando la figura mezcla densidades
    # altas y bajas, S recorre todo [0, 1] y conviene el eje entero; si no, se
    # recorta a la izquierda para que se vea la estructura cerca de S = 1.
    axes.set_xlim(0.0, 1.005) if full else axes.set_xlim(right=1.005)
    axes.legend(loc="best")
    common.save(figure, folder, name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--items", default="c,d,e,f",
                        help="items del enunciado a generar, separados por coma. "
                             "El estudio extendido de clusters usa --items d,e,f, "
                             "porque las densidades 1/(k*pi) solo entran ahi.")
    parser.add_argument("--sweeps",
                        help="varios barridos separados por coma: sus resumenes se "
                             "unen y las curvas de todas las densidades entran en la "
                             "misma figura. Pisa a --sweep.")
    parser.add_argument("--rhos",
                        help="densidades a graficar, separadas por coma y en el orden "
                             "en que van a la leyenda. Por defecto, todas las del "
                             "barrido, de menor a mayor.")
    parser.add_argument("--pares", action="store_true",
                        help="ademas, la comparacion Vicsek-votante de a una densidad "
                             "por figura (item f). Es lo que hace el barrido principal.")
    parser.add_argument("--resaltar",
                        help="puntos a rodear con un aro en las curvas contra eta, "
                             "como 'vicsek:4:0.5,voter:4:4' (modelo:rho:eta). Son las "
                             "configuraciones que la presentacion muestra animadas.")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    items = {piece.strip() for piece in arguments.items.split(",") if piece.strip()}
    unknown = items - set(common.FOLDER_NAME)
    if unknown:
        raise SystemExit(f"item desconocido: {', '.join(sorted(unknown))}")

    common.use_report_style(arguments.estilo)
    sweeps = ([piece.strip() for piece in arguments.sweeps.split(",") if piece.strip()]
              if arguments.sweeps else [arguments.sweep])
    records = common.read_summaries(sweeps)
    realizations = min(record["M"] for record in records)
    available = {record["rho"] for record in records}
    if arguments.rhos:
        rhos = [float(piece) for piece in arguments.rhos.split(",")]
        missing = [rho for rho in rhos
                   if not any(common.close(rho, other) for other in available)]
        if missing:
            raise SystemExit("los barridos indicados no tienen las densidades "
                             + ", ".join(f"{rho:g}" for rho in missing))
    else:
        rhos = sorted(available)
    # Cuando la figura mezcla las densidades del enunciado con las de 1/(k*pi),
    # S recorre todo [0, 1] y los ejes se fijan en ese rango.
    full = common.spans_both_families(rhos)
    tag = f"rho{common.joined_densities(rhos)}_M{realizations}"
    figures = arguments.figures

    highlights = []
    if arguments.resaltar:
        for piece in arguments.resaltar.split(","):
            model, rho, eta = piece.strip().split(":")
            if model not in common.MODEL_LABEL:
                raise SystemExit(f"modelo desconocido en --resaltar: {model}")
            highlights.append((model, float(rho), float(eta)))

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
                              f"{observable}_vs_eta_{model}_{tag}.png", full=full,
                              highlights=highlights)
        for destination in destinations("e", model):
            against_fraction(records, [model], rhos, destination,
                             f"va_vs_S_{model}_{tag}.png", full=full)

    if "f" not in items or not arguments.pares:
        return
    f = common.folder("f", figures)
    for rho in rhos:
        token = common.density_number(rho)
        if "c" in items:
            against_noise(records, ["vicsek", "voter"], [rho], "va", f,
                          f"va_vs_eta_vicsek_vs_voter_rho{token}_M{realizations}.png",
                          highlights=highlights)
        if "d" in items:
            against_noise(records, ["vicsek", "voter"], [rho], "S", f,
                          f"S_vs_eta_vicsek_vs_voter_rho{token}_M{realizations}.png",
                          highlights=highlights)
        if "e" in items:
            against_fraction(records, ["vicsek", "voter"], [rho], f,
                             f"va_vs_S_vicsek_vs_voter_rho{token}_M{realizations}.png")



if __name__ == "__main__":
    main()
