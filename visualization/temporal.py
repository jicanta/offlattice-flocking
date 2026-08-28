"""Items (b), (d) y (f): evolucion temporal de va y de S.

Dos tipos de figura, siempre con dos paneles (va arriba, S abajo):

* Un caso, todas sus realizaciones: las M curvas en gris, el promedio en
  color, la linea vertical en t_eq, y la linea horizontal con su banda que
  son el valor escalar y su desvio, calculados tal como se usan luego en las
  curvas contra eta. Es la figura que explicita como se calcula el escalar.
* Varios casos superpuestos: solo la curva promedio de cada caso, con su t_eq
  y su promedio estacionario. Sirve para comparar ruidos, densidades o
  modelos.

Sin argumentos genera el juego completo de figuras del informe. Con --model,
--rho y --eta genera una figura puntual.

    python3 visualization/temporal.py
    python3 visualization/temporal.py --model voter --rho 4 --eta 0.5
    python3 visualization/temporal.py --model vicsek --rho 4 --etas 0.5,2,4
    python3 visualization/temporal.py --model vicsek --eta 2 --rhos 2,4,8 --item d
"""

from __future__ import annotations

import argparse
from functools import lru_cache

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

import common

GREY = "#9a9a9a"

# Fases distintas del punteado de las verticales: dos casos con el mismo t_eq
# caerian en el mismo pixel y el ultimo dibujado taparia al anterior.
DASH_PHASES = [(phase, (1, 5)) for phase in (0, 2, 4, 1, 3, 5)]

# Que significan la vertical punteada y la horizontal a trazos. En las figuras
# de un solo caso cada trazo ya lleva su etiqueta; en las superpuestas no se
# puede, porque habria una por serie, asi que se explican una sola vez.
CONVENTION = [
    Line2D([], [], color=GREY, linestyle=":", linewidth=1.2,
           label="inicio del estacionario ($t_{eq}$)"),
    Line2D([], [], color=GREY, linestyle="--", linewidth=1.0,
           label="promedio en el estacionario"),
]


class Cases:
    """Carga (y recuerda) las realizaciones de cada caso del barrido."""

    def __init__(self, sweep):
        self.grouped = common.group_runs(common.read_index(sweep))

    @lru_cache(maxsize=None)
    def stack(self, model: str, rho: float, eta: float) -> np.ndarray:
        return common.load_case(common.find_case(self.grouped, model, rho, eta))

    def realizations(self) -> int:
        return min(len(group) for group in self.grouped.values())


def new_figure():
    figure, panels = plt.subplots(2, 1, sharex=True, figsize=(7.6, 6.4))
    panels[0].set_ylabel(common.LABEL["va"])
    panels[0].set_ylim(0.0, 1.05)
    panels[1].set_ylabel(common.LABEL["S"])
    panels[1].set_xlabel("$t$ [s]")
    return figure, panels


def single_case(cases: Cases, model: str, rho: float, eta: float, folder) -> None:
    stack = cases.stack(model, rho, eta)
    result = common.analyse_case(stack)
    time = stack[0, :, 0]
    start = result["start"]

    figure, panels = new_figure()
    color = common.MODEL_STYLE[model]["color"]
    for axes, observable in zip(panels, ("va", "S")):
        column = common.COLUMN[observable]
        for index in range(stack.shape[0]):
            axes.plot(time, stack[index, :, column], color=GREY, linewidth=0.5, alpha=0.45,
                      label=f"realizaciones ($M$ = {result['M']})" if index == 0 else None)
        axes.plot(time, stack[:, :, column].mean(axis=0), color=color, linewidth=1.6,
                  label="promedio de las realizaciones")
        axes.axvline(time[start], color="black", linestyle=":", linewidth=1.4,
                     label=f"$t_{{eq}}$ = {time[start]:.0f}")
        mean, deviation = result[observable], result[f"{observable}_std"]
        axes.hlines(mean, time[start], time[-1], color="black", linestyle="--", linewidth=1.3,
                    label=f"$\\langle {common.LABEL[observable][1:-1]} \\rangle$ = "
                          f"{mean:.3f} $\\pm$ {deviation:.3f}")
        axes.fill_between([time[start], time[-1]], mean - deviation, mean + deviation,
                          color=color, alpha=0.18, linewidth=0)
    panels[0].legend(loc="best", ncol=2, fontsize=10)
    common.save(figure, folder,
                f"va_S_vs_t_{model}_rho{common.density_number(rho)}"
                f"_eta{common.number(eta)}_M{result['M']}.png")


def overlay(cases: Cases, entries: list[tuple], folder, name: str) -> None:
    """entries: [(model, rho, eta, etiqueta, color)]."""
    figure, panels = new_figure()
    realizations = None
    for index, (model, rho, eta, label, color) in enumerate(entries):
        stack = cases.stack(model, rho, eta)
        result = common.analyse_case(stack)
        realizations = result["M"] if realizations is None else min(realizations, result["M"])
        time = stack[0, :, 0]
        start = result["start"]
        style = common.MODEL_STYLE[model]["linestyle"]
        for axes, observable in zip(panels, ("va", "S")):
            column = common.COLUMN[observable]
            # El t_eq va en la etiqueta: si dos verticales coinciden, el valor
            # sigue estando escrito aunque una tape a la otra.
            axes.plot(time, stack[:, :, column].mean(axis=0), color=color, linewidth=1.3,
                      linestyle=style,
                      label=f"{label} · $t_{{eq}}$ = {time[start]:.0f}")
            axes.axvline(time[start], color=color, linewidth=1.2,
                         linestyle=DASH_PHASES[index % len(DASH_PHASES)])
            axes.hlines(result[observable], time[start], time[-1], color=color,
                        linestyle="--", linewidth=1.0, alpha=0.8)
    # Dos leyendas en paneles distintos: las series arriba del area de datos,
    # porque las curvas ocupan todo el ancho, y la convencion de trazos dentro
    # del panel de S, que es el que suele tener lugar libre.
    panels[0].legend(loc="lower center", bbox_to_anchor=(0.5, 1.01),
                     ncol=min(len(entries), 3), frameon=False, fontsize=11)
    panels[1].legend(handles=CONVENTION, loc="best", fontsize=9)
    common.save(figure, folder, name.replace("{M}", str(realizations)))


def standard_set(cases: Cases, figures) -> None:
    low, high = 0.5, 4.0
    eta_set = [0.5, 1.0, 2.0, 3.0, 4.0]
    rhos = [2.0, 4.0, 8.0]
    eta_colors = plt.cm.viridis(np.linspace(0.05, 0.85, len(eta_set)))

    for model in ("vicsek", "voter"):
        # (b) para Vicsek; (f) repite (b) para el votante.
        item = common.folder("b" if model == "vicsek" else "f", figures)
        for rho in rhos:
            for eta in (low, high):
                single_case(cases, model, rho, eta, item)
            overlay(cases,
                    [(model, rho, eta, f"$\\eta$ = {eta:g}", color)
                     for eta, color in zip(eta_set, eta_colors)],
                    item,
                    f"va_S_vs_t_{model}_rho{common.density_number(rho)}"
                    f"_etas{common.joined(eta_set)}_promedioM{{M}}.png")
        # (d) S(t) para las tres densidades; (f) lo repite para el votante.
        item = common.folder("d" if model == "vicsek" else "f", figures)
        for eta in (low, 2.0, high):
            overlay(cases,
                    [(model, rho, eta, f"$\\rho$ = {common.density_label(rho)}",
                      common.density_color(rho))
                     for rho in rhos],
                    item,
                    f"va_S_vs_t_{model}_eta{common.number(eta)}"
                    f"_rhos{common.joined_densities(rhos)}_promedioM{{M}}.png")

    # (f) comparacion directa entre modelos, misma densidad y mismo ruido.
    item = common.folder("f", figures)
    for rho in rhos:
        for eta in (low, 2.0):
            overlay(cases,
                    [(model, rho, eta, common.MODEL_LABEL[model], common.MODEL_STYLE[model]["color"])
                     for model in ("vicsek", "voter")],
                    item,
                    f"va_S_vs_t_vicsek_vs_voter_rho{common.density_number(rho)}"
                    f"_eta{common.number(eta)}_promedioM{{M}}.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", choices=("vicsek", "voter"))
    parser.add_argument("--rho", type=float)
    parser.add_argument("--eta", type=float, help="un caso con todas sus realizaciones")
    parser.add_argument("--etas", help="lista separada por coma: superpone las curvas promedio")
    parser.add_argument("--rhos", help="lista separada por coma: superpone las curvas promedio "
                                       "de esas densidades a un mismo --eta (figura del item d)")
    parser.add_argument("--item", default="b", choices=tuple(common.FOLDER_NAME),
                        help="carpeta de destino de la figura puntual")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    common.use_report_style()
    cases = Cases(arguments.sweep)
    if arguments.model is None:
        standard_set(cases, arguments.figures)
        return
    folder = common.folder(arguments.item, arguments.figures)
    if arguments.rhos:
        if arguments.eta is None:
            raise SystemExit("--rhos necesita un --eta")
        rhos = [float(piece) for piece in arguments.rhos.split(",")]
        overlay(cases,
                [(arguments.model, rho, arguments.eta,
                  f"$\\rho$ = {common.density_label(rho)}", common.density_color(rho))
                 for rho in rhos],
                folder,
                f"va_S_vs_t_{arguments.model}_eta{common.number(arguments.eta)}"
                f"_rhos{common.joined_densities(rhos)}_promedioM{{M}}.png")
        return
    if arguments.rho is None:
        raise SystemExit("--rho es obligatorio junto con --model")
    if arguments.etas:
        etas = [float(piece) for piece in arguments.etas.split(",")]
        colors = plt.cm.viridis(np.linspace(0.05, 0.85, len(etas)))
        overlay(cases,
                [(arguments.model, arguments.rho, eta, f"$\\eta$ = {eta:g}", color)
                 for eta, color in zip(etas, colors)],
                folder,
                f"va_S_vs_t_{arguments.model}_rho{common.density_number(arguments.rho)}"
                f"_etas{common.joined(etas)}_promedioM{{M}}.png")
    elif arguments.eta is not None:
        single_case(cases, arguments.model, arguments.rho, arguments.eta, folder)
    else:
        raise SystemExit("indicar --eta (un caso) o --etas (superposicion)")


if __name__ == "__main__":
    main()
